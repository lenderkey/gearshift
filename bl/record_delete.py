import os

from Context import Context
from structures import FileRecord
import db

import logging as logger

def record_delete(record:FileRecord, authorized:dict):
    """
    """
    import bl

    db.record_delete(record)

    try:
        os.unlink(record.filepath)
    except FileNotFoundError:
        pass

    bl.record_record(record, authorized=authorized, action="delete")
