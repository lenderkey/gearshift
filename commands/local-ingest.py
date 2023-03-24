#
#   commands/ingest.py
#   
#   David Janes
#   Gearshift
#   2023-03-23
#

from Context import Context

import logging as logger
import pprint
import os
import sys

import click

import helpers

L = "local-ingest"

@cli.command("local-ingest", help="Add a file to local Gearshift") # type: ignore
@click.argument("filename", required=True)
@click.option("--dst-name", help="store destination", default=None)
def build(filename, dst_name):
    """
    Ingest a file into the local Gearshift database
    
    Example:
    python gearshift.py --debug ingest gearshift.py --dst-name xxx
    """

    context = Context.instance
    context.ingest_file(filename, dst_name)