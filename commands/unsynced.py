#
#   commands/unsynced.py
#   
#   David Janes
#   Gearshift
#   2023-08-06
#

import db

L = "unsynced"

import logging as logger

@cli.command("unsynced", help="client: list files that are not synced") # type: ignore
def _():
    db.setup()
    for out_record in db.record_list(is_synced=False):
        if out_record.is_deleted:
            print(out_record.filename, "(deleted)")
        else:
            print(out_record.filename)
