#
#   commands/zip.py
#   
#   David Janes
#   Gearshift
#   2023-03-27
#

from Context import Context

import click

L = "dst-zip"

@cli.command("dst-zip", help="Add files from ZIP to local Gearshift") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--input",
              help="file to read from (ZIP))", 
              default="-")
@click.option("--output",
                help="file to write to (YAML)", 
                default="-")
def dst_zip(dry_run:bool, input:str, output:str):
    """
    unzip a file created by src-zip and ingest every file.
    """

    context = Context.instance
