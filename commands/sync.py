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
    context = Context.instance

    out_sync_items = SyncItems()

    max_files = 10
    max_size = 1000 * 1000 * 1000

    count = 0
    size = 0
    for file_record in db.unsynced(): 
        if count >= max_files:
            out_sync_items.more = True
            break
        if size >= max_size:
            out_sync_items.more = True
            break

        count += 1
        size += file_record.size

        out_sync_items.items.append(file_record)

    response = requests.post(
        "http://127.0.0.1:8000/docs/",
        json=out_sync_items.model_dump(),
    )
    in_json = response.json()
    in_sync_items = SyncItems(**in_json)

    zout = io.BytesIO()
    with zipfile.ZipFile(zout, mode="w") as zipper:
        for file_record in in_sync_items.items:
            try:
                with open(file_record.path, "rb") as fin:
                    zipper.writestr(file_record.filename, fin.read())
            except IOError:
                logger.exception(f"{L}: unexpected error with in_file={file_record.path}")

    zipped = zout.getvalue()
    print("SENDING", len(zipped))

    response = requests.post(
        "http://127.0.0.1:8000/docs/",
        data=zipped,
        headers={
            "Content-Type": "application/octet-stream",
        },
    )
    print(response)

    ## print(in_sync_items)

    ## print(yaml.dump(infod))
    '''


    zout = io.BytesIO()
    with zipfile.ZipFile(zout, mode="w") as zipper:
        for record in data.get("records", []):
            data_hash = record.get("data_hash")
            src_name = record.get("filename")
            if not data_hash or not src_name:
                continue

            if os.path.isabs(src_name):
                logger.error(f"{L}: filename must be relative: {src_name}")
                continue

            in_file = context.src_path(src_name)
            if not os.path.exists(in_file):
                logger.error(f"{L}: file does not exist: {in_file}")
                continue

            try:
                with open(in_file, "rb") as fin:
                    zipper.writestr(src_name, fin.read())
            except IOError:
                logger.exception(f"{L}: unexpected error with in_file={in_file}")

    if output == "-":
        sys.stdout.buffer.write(zout.getvalue())
    else:
        with open(output, "wb") as fout:
            fout.write(zout.getvalue())
    '''
