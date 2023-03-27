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
@click.option("--filename",
              help="file", 
              default="-")
def src_zip(dry_run:bool, filename:str):
    context = Context.instance

    if filename == "-":
        data = yaml.safe_load(sys.stdin)
    else:
        with open(filename) as fp:
            data = yaml.safe_load(fp)

    zout = io.BytesIO()
    with zipfile.ZipFile(zout, mode="w") as zipper:
        for record in data.get("records", []):
            data_hash = record.get("data_hash")
            src_name = record.get("filename")
            if not data_hash or not filename:
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
                    zipper.writestr(os.path.join("store", src_name), fin.read())
            except IOError:
                logger.exception(f"{L}: unexpected error with in_file={in_file}")

    with open("xxx.zip", "wb") as fout:
        fout.write(zout.getvalue())
