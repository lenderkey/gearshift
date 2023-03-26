#
#   commands/src-zip.py
#   
#   David Janes
#   Gearshift
#   2023-03-24
#

from Context import Context

import logging as logger

import click

import yaml
import sys

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

    nrecords = []
    for record in data.get("records", []):
        if record.get("is_deleted"):
            continue

        data_hash = record.get("data_hash")
        if not data_hash:
            continue

        if context.dst_has_hash(data_hash):
            continue

        nrecords.append(record)

    data["records"] = nrecords

    print(yaml.dump(data))
