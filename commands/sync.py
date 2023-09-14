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
import click
import random
import re
from structures import SyncRequest

L = "sync"

import logging
logger = logging.getLogger(__name__)

def do_up(max_files:int=10, max_size:int=10 * 1000 * 1000):
    import bl

    logger.info(f"{L}: do up")

    started = time.time()

    iterator = db.record_list(is_synced=False)

    db.start()

    ncycles = 0
    nrecords = 0

    out_record = next(iterator, None)
    while out_record:
        ncycles += 1
        out_sync_items = SyncRequest()

        count = 0
        size = 0
        outd = {}

        while out_record:
            out_sync_items.records.append(out_record)
            outd[out_record.filename] = out_record
            nrecords += 1

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
            
        response = requests.post(
            Context.instance.src_url,
            json=out_sync_items.model_dump(mode="json", exclude=["aes_iv", "aes_tag", "key_hash", "seen"]),
            headers={
                **bl.authorization_header(),
            },
        )
        if response.status_code != 200:
            logger.error(f"{L}: unexpected status_code={response.status_code}")
            break

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
                    **bl.authorization_header(),
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

    logger.info(f"{L}: finished {time.time() - started:.4f}s {ncycles=} {nrecords=}")

def do_down():
    import helpers
    import bl

    logger.info(f"{L}: do down")

    since_added = ""
    while True:
        ## get the next batch of files to sync
        response = requests.get(
            Context.instance.src_url,
            params={
                "limit": 5,
                "added": since_added,
            },
            headers={
                **bl.authorization_header(),
            },
        )
        if response.status_code != 200:
            logger.error(f"{L}: unexpected status_code={response.status_code}")
            break

        in_json = response.json()

        in_sync_items = SyncRequest(**in_json)
        if not in_sync_items.records:
            logger.debug(f"{L}: no records returned - can stop")
            break

        ## figure out which files we want
        down_sync_items = SyncRequest()

        for item in in_sync_items.records:
            record = db.record_get(item)

            if item.is_deleted:
                logger.info(f"{L}: DELETE {item}")
                if not record or not record.is_deleted:
                    db.record_delete(item)

                    try:
                        os.unlink(item.filepath)
                    except FileNotFoundError:
                        pass

                continue

            if not record:
                logger.info(f"{L}: NEW {item}")
                down_sync_items.records.append(item)
                continue

            if record.data_hash == item.data_hash:
                logger.debug(f"{L}: already have {item}")
                continue

            logger.info(f"{L}: UDPATE {item}")
            down_sync_items.records.append(item)

        ## print(down_sync_items.records)
                
        ## request those files
        if down_sync_items.records:
            ## print(down_sync_items)
            response = requests.post(
                Context.instance.src_url,
                params={
                    "action": "pull-zip",
                },
                json=down_sync_items.model_dump(mode="json", exclude=["aes_iv", "aes_tag", "key_hash", "seen"]),
                headers={
                    **bl.authorization_header(),
                },
            )
            if response.status_code != 200:
                logger.error(f"{L}: unexpected status_code={response.status_code}")
                break

            data = response.content
            ## print("HERE:XXX", len(data))
            zipper = zipfile.ZipFile(io.BytesIO(data), mode="r")
            for dst_name in zipper.namelist():
                data = zipper.read(dst_name)
                record = bl.data_analyze(dst_name, data=data)

                postfix = f".{random.randint(100000, 999999)}"

                try:
                    os.makedirs(os.path.dirname(record.filepath), exist_ok=True)

                    with open(record.filepath + postfix, "wb") as fout:
                        fout.write(data)

                    os.rename(record.filepath + postfix, record.filepath)
                    logger.info(f"{L}: wrote {record.filepath} bytes={len(data)}")

                    db.start()
                    db.record_put(record)
                    db.commit()
                except:
                    try: os.remove(record.filepath + postfix)
                    except: pass

                    logger.exception(f"{L}: unexpected error with in_file={record.filepath}")
                    break

            ## break

        ## figure out the next batch of files to sync
        max_added = ""
        for item in in_sync_items.records:
            item_added = helpers.format_datetime(item.added)
            if item_added < since_added:
                logger.error("unexpected: {item.added=} < {since_added=}")
                break

            max_added = max(max_added, item_added)

        if max_added <= since_added:
            logger.error("unexpected: {max_added=} <= {since_added=}")
            break

        since_added = max_added

        ## nothing left to do
        if not in_sync_items.more:
            break

@cli.command("sync", help="") # type: ignore
@click.option("--up/--no-up", is_flag=True, default=True, help="Upload files to remote")
@click.option("--down/--no-down", is_flag=True, default=True, help="Download files from remote")
def sync(up: bool, down: bool):
    db.setup()

    if up:
        do_up()
    if down:
        do_down()



