import os

from Context import Context
from structures import FileRecord
import db

import logging as logger

def record_delete(record:FileRecord, authorized:dict):
    """
    """

    db.record_delete(in_record)

    try:
        os.unlink(record.filepath)
    except FileNotFoundError:
        pass
