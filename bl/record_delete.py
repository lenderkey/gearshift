import os

from Context import Context
from structures import FileRecord, Token, Connection
import db

import logging as logger

def record_delete(record:FileRecord, token:Token, connection:Connection):
    """
    """
    import bl

    db.record_delete(record)

    try:
        os.unlink(record.filepath)
    except FileNotFoundError:
        pass

    bl.record_record(record, token=token, connection=connection, action="delete")
