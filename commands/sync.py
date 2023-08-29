#
#   commands/sync.py
#   
#   David Janes
#   Gearshift
#   2023-08-29
#

from Context import Context

import io
import os
import zipfile
import yaml
import pprint
import requests
import db
from structures import SyncItems

L = "sync"

import logging as logger

@cli.command("sync", help="") # type: ignore
def dst_zip():
    max_files = 10
    max_size = 1000 * 1000 * 1000

    iterator = db.unsynced()

    out_item = next(iterator, None)
    while out_item:
        out_sync_items = SyncItems()

        count = 0
        size = 0

        while out_item:
            out_sync_items.items.append(out_item)

            count += 1
            size += out_item.size

            out_item = next(iterator, None)
            if not out_item:
                break

            if count >= max_files:
                out_sync_items.more = True
                break

            if size >= max_size:
                out_sync_items.more = True
                break
            
        response = requests.post(
            "http://127.0.0.1:8000/docs/",
            json=out_sync_items.model_dump(),
        )
        in_json = response.json()
        in_sync_items = SyncItems(**in_json)

        if len(in_sync_items.items) == 0:
            break

        zout = io.BytesIO()
        with zipfile.ZipFile(zout, mode="w") as zipper:
            for in_item in in_sync_items.items:
                try:
                    with open(in_item.filepath, "rb") as fin:
                        zipper.writestr(in_item.filename, fin.read())
                except IOError:
                    logger.exception(f"{L}: unexpected error with in_file={in_item.filepath}")

        zipped = zout.getvalue()
        print("SENDING", len(zipped), count, size)

        response = requests.post(
            "http://127.0.0.1:8000/docs/",
            data=zipped,
            headers={
                "Content-Type": "application/octet-stream",
            },
        )
        if response.status_code != 200:
            logger.error(f"{L}: unexpected status_code={response.status_code}")
            break


        ## not ready for loops yet
        ## break