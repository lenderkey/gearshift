
from Context import Context
from structures import SyncRequest, Connection
import db
import datetime

def pull_json(
    since_added:str|datetime.datetime|None=None, 
    limit:int=None, max_size:int = 10 * 1000 * 1000, 
    connection:Connection=None,
) -> SyncRequest:
    out_sync_items = SyncRequest()

    if not limit:
        limit = 1000

    count = 0
    nbytes = 0

    for item in db.record_list(order_by="added", since_added=since_added, limit=limit):
        ## none of your business, client
        item.key_hash = None
        item.is_synced = None

        out_sync_items.records.append(item)

        count += 1
        nbytes += item.size
        ## print("HERE:COUNT", count, nbytes, max_size)

        if nbytes >= max_size:
            out_sync_items.more = True
            break

        if count == limit:
            out_sync_items.more = True
            break

    ## print("HERE:NITEM", len(out_sync_items.records))
    return out_sync_items
