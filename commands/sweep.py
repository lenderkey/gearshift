#
#   commands/sweep.py
#   
#   David Janes
#   Gearshift
#   2023-08-23
#

from Context import Context
from structures.FileRecord import FileRecord

import logging as logger
import pprint

import click
import sys
import time

import helpers
import db
import bl

L = "sweep"

@cli.command("sweep", help="Build a Gearshift Database") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
def src_build(dry_run):
    """
    Build a Gearshift Database
    
    Example:
    ./gearshift sweep
    """

    context = Context.instance
    logger.info(f"{L}: started {context.src_root=}")

    if dry_run:
        for filename in helpers.walker():
            pprint.pprint(helpers.analyze(filename))
    else:
        start = time.time()

        db.setup()
        db.start()

        rcount = 0
        icount = 0

        for filename in helpers.walker():
            icount += db.put_record(bl.file_analyze(Context.instance, filename))
            rcount += 1

        deleted = db.mark_deleted(cutoff=start, force=True)
        ## deleted = 0
        db.commit()

        logger.info(f"{L}: files={rcount} inserted={icount} deleted={deleted}")
