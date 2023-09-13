import os

from Context import Context
from structures import FileRecord, Token, Connection
import db

import logging as logger

def record_put(record:FileRecord, data:bytes, token:Token, connection:Connection):
    """
    """
    import bl

    record = record.clone()

    context = Context.instance
    key_hash = context.server_key_hash()
    if key_hash:
        record.key_hash = key_hash

    db.start()
    record = bl.record_ingest(record, data=data)
    record = db.record_put(record)
    bl.record_record(record, token=token, connection=connection, action="put")
    db.commit()
