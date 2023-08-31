import os
import zipfile
import io

from Context import Context
from structures import SyncItems
import bl
import db

def pushed_json(raw_json:dict) -> dict:
    """
    """
    out_sync_items = SyncItems()
    in_sync_items = SyncItems(**raw_json)
    for item in in_sync_items.items:
        if item.is_deleted:
            ## mark record deleted and delete the file
            db.put_record(item, touch_only=False)
            bl.record_delete(item)
        elif db.put_record(item, touch_only=True):
            ## file has changed - ask for it
            item.is_synced = False
            out_sync_items.items.append(item)
        else:
            ## file has not changed
            pass

    return out_sync_items
