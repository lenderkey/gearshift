#
#   commands/ingest.py
#   
#   David Janes
#   Gearshift
#   2023-09-23
#

from Context import Context

import logging as logger
import pprint
import os
import sys

import click

import helpers

L = "build"

@cli.command("ingest", help="Add a file to local Gearshift") # type: ignore
@click.argument("filename", required=True)
@click.option("--dst-name", help="store destination", default=None)
def build(filename, dst_name):
    context = Context.instance

    context.ingest_file(filename, dst_name)
