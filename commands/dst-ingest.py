#
#   commands/ingest.py
#   
#   David Janes
#   Gearshift
#   2023-03-23
#

from Context import Context

import click

L = "dst-ingest"

@cli.command("dst-ingest", help="Add a file to local Gearshift") # type: ignore
@click.argument("filename", required=True)
@click.option("--dst-name", help="store destination", default=None)
def dst_ingest(filename, dst_name):
    """
    Ingest a file into the local Gearshift database. 
    Note normally you don't need to use this.
    
    Example:
    python gearshift.py --debug ingest gearshift.py --dst-name xxx
    """

    context = Context.instance
    data_hash, is_new = context.ingest_file(filename)

    if dst_name:
        context.ingest_link(data_hash, dst_name)
