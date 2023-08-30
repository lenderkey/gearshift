#
#   commands/zip.py
#   
#   David Janes
#   Gearshift
#   2023-03-27
#

from Context import Context

import click

import sys
import os
import io
import zipfile

import logging as logger

L = "dst-zip"

@cli.command("dst-zip", help="Add files from ZIP to local Gearshift") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--input",
              help="file to read from (ZIP))", 
              default="-")
@click.option("--output",
                help="file to write to (YAML)", 
                default="-")
def dst_zip(dry_run:bool, input:str, output:str):
    """
    unzip a file created by src-zip and ingest every file.
    """

    context = Context.instance

    if input == "-":
        zin = sys.stdin.buffer
    else:
        zin = open(input, "rb")

    with zipfile.ZipFile(zin, mode="r") as zipper:
        for dst_name in zipper.namelist():
            if os.path.isabs(dst_name):
                logger.error(f"{L}: filename must be relative: {dst_name}")
                continue

            data_hash, is_new = context.ingest_data(dst_name, data=zipper.read(dst_name))

            context.ingest_link(data_hash, dst_name)

            '''

            out_file = context.dst_path(name)
            if os.path.exists(out_file):
                logger.error(f"{L}: file already exists: {out_file}")
                continue

            if not dry_run:
                with open(out_file, "wb") as fout:
                    fout.write(zipper.read(name))

            context.ingest_link(context.data_hash(out_file), name)            
            '''
