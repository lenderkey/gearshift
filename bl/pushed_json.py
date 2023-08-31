import os
import zipfile
import io

from Context import Context
from structures import SyncRequest
import bl
import db

def pushed_json(raw_json:dict) -> dict:
    """
    """
    out_sync_items = SyncRequest()
    in_sync_items = SyncRequest(**raw_json)
    for item in in_sync_items.records:
        if item.is_deleted:
            ## mark record deleted and delete the file
            db.record_put(item, touch_only=False)
            bl.record_delete(item)
        elif db.record_put(item, touch_only=True):
            ## file has changed - ask for it
            item.is_synced = False
            out_sync_items.records.append(item)
        else:
            ## file has not changed
            pass

    return out_sync_items
