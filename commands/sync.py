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

    db.start()

    out_record = next(iterator, None)
    while out_record:
        out_sync_items = SyncRequest()

        count = 0
        size = 0
        outd = {}

        while out_record:
            out_sync_items.records.append(out_record)
            outd[out_record.filename] = out_record

            count += 1
            size += out_record.size

            out_record = next(iterator, None)
            if not out_record:
                break

            if count >= max_files:
                out_sync_items.more = True
                break

            if size >= max_size:
                out_sync_items.more = True
                break
            
        ## "A.1", list(outd.keys()))
        response = requests.post(
            "http://127.0.0.1:8000/docs/",
            json=out_sync_items.model_dump(),
        )
        in_json = response.json()
        in_sync_items = SyncRequest(**in_json)

        ## if marked as synced, update the database - we do not need to do anything else
        for in_record in in_sync_items.records:
            if not in_record.is_synced:
                continue
        
            _record = outd.get(in_record.filename)
            if not _record:
                logger.warning(f"{L}: unexpected record={in_record.filename} - not in original message")
                continue

            _record.is_synced = True
            db.record_put(_record)

        ## if not mentioned in response, we can also assume they are synced
        for in_record in in_sync_items.records:
            try: del outd[in_record.filename]
            except KeyError: pass

        ## print("A")
        for _record in outd.values():
            ## print("B")
            _record.is_synced = True
            db.record_put(_record)

        ## make a zip of all files that are neede
        zcount = 0
        zout = io.BytesIO()
        zipped = None
        with zipfile.ZipFile(zout, mode="w") as zipper:
            for in_record in in_sync_items.records:
                if in_record.is_synced:
                    continue

                try:
                    with open(in_record.filepath, "rb") as fin:
                        zipper.writestr(in_record.filename, fin.read())
                        zcount += 1
                except IOError:
                    logger.exception(f"{L}: unexpected error with in_file={in_record.filepath}")

            zipper.close()
            zipped = zout.getvalue()
            ## print(zipped)

        if zcount and zipped:
            logger.info(f"{L}: zipped={len(zipped)} files={zcount}")

            response = requests.post(
                Context.instance.src_url,
                data=zipped,
                headers={
                    "Content-Type": "application/zip",
                },
            )
            ## print(response.headers, response.raw)
            if response.status_code != 200:
                logger.error(f"{L}: unexpected status_code={response.status_code}")
                break

        ## mark remaining records (the ones we just uploaded) as synced
        for in_record in in_sync_items.records:
            if in_record.is_synced:
                continue
        
            _record = outd.get(in_record.filename)
            if not _record:
                continue

            _record.is_synced = True
            db.record_put(_record)

    db.commit()


    logger.info(f"{L}: finished {time.time() - started:.4f}s")