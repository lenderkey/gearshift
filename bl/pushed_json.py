import os
import zipfile
import io

from Context import Context
from structures import SyncItems
import bl
import db

def pushed_json(context:Context, raw_json:dict) -> dict:
    out_sync_items = SyncItems()
    in_sync_items = SyncItems(**raw_json)
    for item in in_sync_items.items:
        if not db.put_record(item, touch_only=True):
            continue

        out_sync_items.items.append(item)
        print("WANT", item)

    ## print("out_sync_items", out_sync_items)
    return out_sync_items
