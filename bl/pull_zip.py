import os
import zipfile
import io

from Context import Context
from structures import SyncRequest, Token, Connection
import bl
import db

L = "pull_zip"

import zipfile
import logging as logger

def pull_zip(raw_json:bytes, token:Token, connection:Connection) -> bytes:
    """
    SERVER side when the CLIENT sends a SyncRequest for ZIP file
    """
    ## print("PULL ZIP", len(raw_json))

    pull_sync_items = SyncRequest(**raw_json)

    zcount = 0
    zout = io.BytesIO()
    zipped = None

    with zipfile.ZipFile(zout, mode="w") as zipper:
        for in_record in pull_sync_items.records:
            in_record = db.record_get(in_record)
            if not in_record or in_record.is_deleted:
                continue
            
            try:
                data = bl.record_digest(in_record)
                zipper.writestr(in_record.filename, data)
                zcount += 1
            except IOError:
                logger.exception(f"{L}: unexpected error with in_file={in_record.filepath}")

        zipper.close()
        zipped = zout.getvalue()

    return zipped
