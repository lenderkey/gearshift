
from Context import Context
from structures import SyncRequest
import db

def pull_json() -> dict | SyncRequest:
    out_sync_items = SyncRequest()

    for item in db.list():
        out_sync_items.records.append(item)

    return out_sync_items
