#
#   commands/build.py
#   
#   David Janes
#   Gearshift
#   2023-0903-23
#

from Context import Context
from FileRecord import FileRecord

import logging as logger
import pprint

import click

import helpers
import db

L = "src-build"

@cli.command("src-build", help="Build a Gearshift Database") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
def src_build(dry_run):
    """
    Build a Gearshift Database
    
    Example:
    python gearshift.py --debug build
    """

    context = Context.instance
    logger.info(f"{L}: started {context.src_root_path=}")

    if dry_run:
        for filename in helpers.walker():
            pprint.pprint(helpers.analyze(filename))
    else:
        db.setup()
        db.start()

        rcount = 0
        icount = 0

        for filename in helpers.walker():
            icount += db.put_record(FileRecord.analyze(filename))
            rcount += 1

        db.commit()

        logger.info(f"{L}: files={rcount} inserted={icount}")


