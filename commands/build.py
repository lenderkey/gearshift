#
#   commands/build.py
#   
#   David Janes
#   Gearshift
#   2023-09-23
#

import click
import logging as logger

L = "build"

@cli.command("build", help="Build a Gearshift Database") # type: ignore
@click.option("--quit-on-error/--no-quit-on-error", is_flag=True)
@click.option("--csv", help="use CSV logger to this file")
def build(quit_on_error, csv):

    logger.info(f"{L}: started")
