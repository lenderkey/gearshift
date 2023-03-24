#
#   commands/checksync.py
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

L = "local-sync"

@cli.command("local-sync", help="Check which records have been synced") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--max-size", help="max size of files (may be exceeded if 1 file)", 
              type=int,
              default=10 * 1000 * 1000)
@click.option("--max-files", help="max number of files", 
              type=int,
              default=1000)
def checksync(dry_run:bool, max_size:int, max_files:int):
    print("records:")

    count = 0
    size = 0
    more = False
    for record in db.checksync(): 
        if count >= max_files:
            more = True
            break
        if size >= max_size:
            more = True
            break

        count += 1
        size += record.size

        print("- filename:", json.dumps(record.filename))
        print(f'  data_hash: "{record.data_hash}"')

        if record.is_deleted:
            print("  is_deleted: true")

    if more:
        print("more: true")
