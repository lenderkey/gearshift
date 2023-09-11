
from Context import Context
from structures import SyncRequest, Connection
import db
import datetime

def pull_json(since_added:str|datetime.datetime|None=None, limit:int=None, connection:Connection=None) -> SyncRequest:
    out_sync_items = SyncRequest()

    if not limit:
        limit = 1000

    count = 0
    for item in db.record_list(order_by="added", since_added=since_added, limit=limit):
        out_sync_items.records.append(item)

        count += 1
        if count == limit:
            out_sync_items.more = True
            break

    return out_sync_items
