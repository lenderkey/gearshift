#
#   commands/download.py
#   
#   David Janes
#   Gearshift
#   2023-03-24
#

from Context import Context

import logging as logger
import pprint
import json
import click

import helpers
import db

L = "unsynced"

@cli.command("unsynced", help="Return unsynced records") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--max-size", help="max size of files (may be exceeded if 1 file)", 
              type=int,
              default=10 * 1000 * 1000)
@click.option("--max-files", help="max number of files", 
              type=int,
              default=1000)
def unsynced(dry_run:bool, max_size:int, max_files:int):
    print("records:")

    count = 0
    size = 0
    for record in db.unsynced(): 
        count += 1
        size += record.size

        print("- filename:", json.dumps(record.filename))
        print(f'  data_hash: "{record.data_hash}"')

        if count >= max_files:
            break
        if size >= max_size:
            break
