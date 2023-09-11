import os

from Context import Context
from structures import FileRecord, Token, Connection
import db

import logging as logger

def record_put(record:FileRecord, data:bytes, token:Token, connection:Connection):
    """
    """
    import bl

    bl.record_ingest(record, data=data)
    db.record_put(record)
    bl.record_record(record, token=token, connection=connection, action="put")
