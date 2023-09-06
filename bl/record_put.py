import os

from Context import Context
from structures import FileRecord
import db

import logging as logger

def record_put(record:FileRecord, data:bytes, authorized:dict):
    """
    """
    import bl

    bl.record_ingest(record, data=data)
    db.record_put(record)
