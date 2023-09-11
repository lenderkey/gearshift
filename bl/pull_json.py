
from Context import Context
from structures import SyncRequest, Connection
import db
import datetime

def pull_json(added:str|datetime.datetime|None=None, connection:Connection=None) -> SyncRequest:
    out_sync_items = SyncRequest()

    for item in db.record_list(order_by="added", since_added=added):
        out_sync_items.records.append(item)

    return out_sync_items
