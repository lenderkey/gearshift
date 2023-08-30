#
#   commands/unsynced.py
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
import sys

L = "src-sync"

@cli.command("src-sync", help="Return unsynced records") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--max-size", help="max size of files (may be exceeded if 1 file)", 
              type=int,
              default=10 * 1000 * 1000)
@click.option("--max-files", help="max number of files", 
              type=int,
              default=1000)
@click.option("--output",
                help="file to write to (YAML)", 
                default="-")
def src_sync(dry_run:bool, max_size:int, max_files:int, output:str):
    if output == "-":
        fout = sys.stdout
    else:
        fout = open(output, "w")

    print("records:", file=fout)

    count = 0
    size = 0
    more = False
    for record in db.list(is_synced=False): 
        if count >= max_files:
            more = True
            break
        if size >= max_size:
            more = True
            break

        count += 1
        size += record.size

        print("- filename:", json.dumps(record.filename), file=fout)
        print(f'  data_hash: "{record.data_hash}"', file=fout)

        if record.is_deleted:
            print("  is_deleted: true", file=fout)

    if more:
        print("more: true", file=fout)
              
    if output != "-":
        fout.close()
        logger.info(f"{L}: wrote {output}")
