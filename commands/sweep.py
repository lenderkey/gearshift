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

@cli.command("sweep", help="client: build a Gearshift db of files") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
def sweep(dry_run):
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
        start = helpers.now()

        db.setup()
        db.start()

        rcount = 0
        icount = 0

        for filename in helpers.walker():
            rcount += 1

            file_record = bl.file_analyze(filename)
            current_record = db.record_get(file_record)
            if current_record:
                db.record_touch(current_record)
                continue

            db.record_put(file_record)
            icount += 1

        deleted = db.mark_deleted(cutoff=start, force=True)
        db.commit()

        logger.info(f"{L}: files={rcount} inserted={icount} deleted={deleted}")
