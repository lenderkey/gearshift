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
import time
import requests
import db
from structures import SyncRequest

L = "sync"

import logging as logger

@cli.command("sync", help="") # type: ignore
def sync():
    max_files = 10
    max_size = 1000 * 1000 * 1000

    started = time.time()
    db.setup()
    iterator = db.list(is_synced=False)

    out_item = next(iterator, None)
    while out_item:
        out_sync_items = SyncRequest()

        count = 0
        size = 0

        while out_item:
            out_sync_items.records.append(out_item)

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
        in_sync_items = SyncRequest(**in_json)

        if len(in_sync_items.records) == 0:
            break

        zout = io.BytesIO()
        with zipfile.ZipFile(zout, mode="w") as zipper:
            for in_item in in_sync_items.records:
                try:
                    with open(in_item.filepath, "rb") as fin:
                        zipper.writestr(in_item.filename, fin.read())
                except IOError:
                    logger.exception(f"{L}: unexpected error with in_file={in_item.filepath}")

        zipped = zout.getvalue()
        logger.info(f"{L}: zipped={len(zipped)} files={count}")

        response = requests.post(
            Context.instance.src_url,
            data=zipped,
            headers={
                "Content-Type": "application/zip",
            },
        )
        if response.status_code != 200:
            logger.error(f"{L}: unexpected status_code={response.status_code}")
            break

    logger.info(f"{L}: finished {time.time() - started:.4f}s")