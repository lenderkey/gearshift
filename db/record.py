#
#   db/record.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

from typing import TypeAlias, Literal

from Context import Context
from structures import FileRecord
import helpers

import logging as logger

GetMode: TypeAlias = Literal["filename,data_hash", "filename", "data_hash" ]

def record_get(record:FileRecord, mode:GetMode="filename,data_hash") -> FileRecord:
    """
    Retrieve a record where the filename and data_hash match.
    """
    
    cursor = Context.instance.cursor()

    query = """\
SELECT 
    filename, data_hash, key_hash, aes_iv, aes_tag, size, is_synced, is_deleted, added 
FROM records 
"""
    params = []

    match mode:
        case "filename,data_hash":
            query += "WHERE filename=? AND data_hash=?"
            params = [ record.filename, record.data_hash ]

        case "filename":
            query += "WHERE filename=?"
            params = [ record.filename ]

        case "data_hash":
            query += "WHERE data_hash=?"
            params = [ record.data_hash ]

        case _:
            raise ValueError(f"unknown mode: {mode}")

    cursor.execute(query, params)

    row = cursor.fetchone()
    if not row:
        return
    
    filename, data_hash, key_hash, aes_iv, aes_tag, size, is_synced, is_deleted, added = row

    return FileRecord.make(
        filename=filename,
        data_hash=data_hash,
        key_hash=key_hash,
        aes_iv=aes_iv,
        aes_tag=aes_tag,
        size=size,
        added=added,
        is_synced=bool(is_synced),
        is_deleted=bool(is_deleted),
    )

def record_put(record:FileRecord) -> FileRecord:
    """
    """
    L = "db.record_put"

    cursor = Context.instance.cursor()
    now = helpers.now()

    record = record.clone()

    ## keep 'added'
    query = "SELECT added FROM records WHERE filename=?"
    cursor.execute(query, (record.filename, ))
    row = cursor.fetchone()
    if row:
        record.added, = row
    else:
        record.added = now
    
    record.cleanup()

    cursor.execute("""
INSERT OR REPLACE INTO records 
(filename, data_hash, key_hash, aes_iv, aes_tag, size, is_synced, is_deleted, added, seen) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        record.filename, 
        not record.is_deleted and record.data_hash or "", 
        not record.is_deleted and record.key_hash or "", 
        record.aes_iv,
        record.aes_tag,
        not record.is_deleted and record.size or 0, 
        int(record.is_synced), 
        int(record.is_deleted),
        helpers.format_datetime(record.added),
        helpers.format_datetime(now),
    ))
    logger.debug(f"{L}: inserted/updated {record.filename=}")

    return record

def record_touch(record:FileRecord) -> bool:
    L = "db.record_touch"
    cursor = Context.instance.cursor()
    now = helpers.now()

    cursor.execute("""
UPDATE records SET seen = ? WHERE filename = ?""", (
        now,
        record.filename,
    ))                     
    logger.debug(f"{L}: touched {record.filename=}")
    return False

def record_delete(record:FileRecord) -> FileRecord:
    """
    """
    L = "db.record_put"

    cursor = Context.instance.cursor()
    now = helpers.now()

    record = record.clone()

    ## keep 'added'
    query = "SELECT added FROM records WHERE filename=?"
    cursor.execute(query, (record.filename, ))
    row = cursor.fetchone()
    if row:
        record.added, = row
    else:
        record.added = now
    
    record.cleanup()

    cursor.execute("""
INSERT OR REPLACE INTO records 
(filename, data_hash, key_hash, aes_iv, aes_tag, size, is_synced, is_deleted, added, seen) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        record.filename, 
        "", 
        "", 
        None,
        None,
        0, 
        record.is_synced, 
        True,
        helpers.format_datetime(record.added),
        helpers.format_datetime(now),
    ))
    logger.debug(f"{L}: deleted {record.filename=}")

    return record

def record_list(
    is_synced:bool=None, is_deleted:bool=None, 
    since_seen:str=None, since_added:str=None, 
    key_hash:str=None, 
    order_by:str=None,
    order_dir:str="ASC",
    limit:int=None,
):
    """
    Return a list of records
    """
    
    cursor = Context.instance.cursor()

    query = "SELECT filename, data_hash, key_hash, aes_iv, aes_tag, size, is_synced, is_deleted, added FROM records"
    params = []

    extras = []
    if is_synced is not None:
        extras.append("is_synced = ?")
        params.append(int(is_synced))

    if is_deleted is not None:
        extras.append("is_deleted = ?")
        params.append(int(is_deleted))

    if key_hash is not None:
        extras.append("key_hash = ?")
        params.append(key_hash)

    if since_seen is not None:
        extras.append("seen > ?")
        params.append(helpers.format_datetime(since_seen))

    if since_added is not None:
        extras.append("added > ?")
        params.append(helpers.format_datetime(since_added))

    if extras:
        query += " WHERE " + " AND ".join(extras)

    if order_by:
        query += f" ORDER BY {order_by}"

        if order_dir:
            query += " " + order_dir

    if limit:
        query += f" LIMIT ?"
        params.append(limit)

    # Execute the query and fetch the first record
    cursor.execute(query, params)
    while row := cursor.fetchone():
        filename, data_hash, key_hash, aes_iv, aes_tag, size, is_synced, is_deleted, added = row

        yield FileRecord.make(
            filename=filename,
            data_hash=data_hash,
            key_hash=key_hash,
            aes_iv=aes_iv,
            aes_tag=aes_tag,
            size=size,
            is_synced=bool(is_synced),
            is_deleted=bool(is_deleted),
            added=added,
        )

def mark_deleted(cutoff:float, force:bool=False):
    """
    Mark a document as deleted if it has not been seen since_seen the cutoff time.
    """

    cursor = Context.instance.cursor()
    try:            
        if force:
            cursor.execute('''
                UPDATE records SET is_deleted = ?, size = 0 WHERE seen < ? AND is_deleted = ?
            ''', (True, cutoff, False)) 

            return cursor.rowcount
        else:
            cursor.execute('''
                SELECT COUNT(*) FROM records WHERE seen < ? AND is_deleted = ?
            ''', (cutoff, False))

            row = cursor.fetchone()
            return row[0]
    finally:        
        cursor.close()

