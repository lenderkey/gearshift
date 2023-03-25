#
#   commands/remote-zip.py
#   
#   David Janes
#   Gearshift
#   2023-03-24
#

from Context import Context

import logging as logger
import pprint

import click

import helpers
import db

L = "remote-zip"

@cli.command("remote-zip", help="Remote ZIP files") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--max-size", help="max size of files (may be exceeded if 1 file)", 
              type=int,
              default=10 * 1000 * 1000)
@click.option("--max-count", help="max number of files", 
              type=int,
              default=100)
def download(dry_run:bool, max_size:int, max_count:int):
    pass