import os
import zipfile
import io

from Context import Context
from structures import SyncRequest
import bl
import db

def pushed_json(raw_json:dict, authorized:dict) -> dict:
    """
    SERVER side when the CLIENT sends a SyncRequest
    """
    out_sync_items = SyncRequest()
    in_sync_items = SyncRequest(**raw_json)

    for in_record in in_sync_items.records:
        if in_record.is_deleted:
            bl.record_delete(in_record, authorized=authorized)
        elif current_record := db.record_get(in_record):
            db.record_touch(in_record)
        else:
            in_record.is_synced = False
            out_sync_items.records.append(in_record)
            continue

        '''
        Right here we can add a big efficiency by looking for a
        whether the file exists already. However, there are some security
        concerns so we will do this later. Basically we don't
        want people to be able to grab files that they don't have 
        access to by hash.
        '''

    return out_sync_items
