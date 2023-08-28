#
#   commands/sync.py
#   
#   David Janes
#   Gearshift
#   2023-08-29
#

from Context import Context

import yaml
import pprint
import requests
import db
from structures import SyncItems, SyncItem

L = "sync"

@cli.command("sync", help="") # type: ignore
def dst_zip():
    context = Context.instance

    records = []

    sync_items = SyncItems()

    max_files = 10
    max_size = 1000 * 1000 * 1000

    count = 0
    size = 0
    more = False
    for file_record in db.unsynced(): 
        if count >= max_files:
            sync_items.more = True
            break
        if size >= max_size:
            sync_items.more = True
            break

        count += 1
        size += file_record.size

        sync_item = SyncItem(
            filename=file_record.filename,
            data_hash=file_record.data_hash,
        )

        if file_record.is_deleted:
            sync_item.is_deleted

        sync_items.records.append(sync_item)

    response = requests.post(
        "http://127.0.0.1:8000/docs/",
        json=sync_items.model_dump(),
    )
    print(response.json())

    ## print(yaml.dump(infod))



