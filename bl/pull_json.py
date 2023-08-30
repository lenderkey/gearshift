
from Context import Context
from structures import SyncItems
import db

def pull_json(context:Context) -> dict | SyncItems:
    out_sync_items = SyncItems()

    for item in db.list():
        out_sync_items.items.append(item)

    return out_sync_items
