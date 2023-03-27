#
#   commands/unzip.py
#   
#   David Janes
#   Gearshift
#   2023-03-27
#

from Context import Context

import click

L = "dst-unzip"

@cli.command("dst-unzip", help="Add a file to local Gearshift") # type: ignore
@click.argument("filename", required=True, default="-")
@click.option("--dst-name", help="store destination", default=None)
def dst_unzip(filename, dst_name):
    """
    Unzip a file created by src-zip and ingest every file.
    """

    context = Context.instance
