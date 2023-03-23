#
#   commands/build.py
#   
#   David Janes
#   Gearshift
#   2023-09-23
#

from Context import Context

import logging as logger
import pprint

import click

import helpers

L = "build"

@cli.command("build", help="Build a Gearshift Database") # type: ignore
@click.option("--quit-on-error/--no-quit-on-error", is_flag=True)
@click.option("--csv", help="use CSV logger to this file")
def build(quit_on_error, csv):
    context = Context.instance
    logger.info(f"{L}: started {context.src_root_path=}")

    cursor = context.cursor()

    for filename in helpers.walker():
        pprint.pprint(helpers.analyze(filename))