#
#   commands/src-zip.py
#   
#   David Janes
#   Gearshift
#   2023-03-24
#

from Context import Context

import click
import yaml

import os
import sys
import io
import zipfile

import logging as logger

L = "src-zip"

@cli.command("src-zip", help="package files as zip") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--input",
              help="file to read from (YAML))", 
              default="-")
@click.option("--output",
                help="file to write to (ZIP)", 
                default="-")
def src_zip(dry_run:bool, input:str, output:str):
    context = Context.instance

    if input == "-":
        data = yaml.safe_load(sys.stdin)
    else:
        with open(input) as fp:
            data = yaml.safe_load(fp)

    zout = io.BytesIO()
    with zipfile.ZipFile(zout, mode="w") as zipper:
        for record in data.get("records", []):
            data_hash = record.get("data_hash")
            src_name = record.get("filename")
            if not data_hash or not src_name:
                continue

            if os.path.isabs(src_name):
                logger.error(f"{L}: filename must be relative: {src_name}")
                continue

            in_file = context.src_path(src_name)
            if not os.path.exists(in_file):
                logger.error(f"{L}: file does not exist: {in_file}")
                continue

            try:
                with open(in_file, "rb") as fin:
                    zipper.writestr(src_name, fin.read())
            except IOError:
                logger.exception(f"{L}: unexpected error with in_file={in_file}")

    if output == "-":
        sys.stdout.buffer.write(zout.getvalue())
    else:
        with open(output, "wb") as fout:
            fout.write(zout.getvalue())

        logger.info(f"{L}: wrote {output}")
