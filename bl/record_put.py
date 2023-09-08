import os

from Context import Context
from structures import FileRecord, Token
import db

import logging as logger

def record_put(record:FileRecord, data:bytes, token:Token):
    """
    """
    import bl

    bl.record_ingest(record, data=data)
    db.record_put(record)
    bl.record_record(record, token=token, action="put")
