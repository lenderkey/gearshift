#
#   db.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

import time
import sqlite3

from Context import Context
from structures.FileRecord import FileRecord
import helpers

import logging as logger

def setup() -> None:
    cursor = Context.instance.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            filename TEXT PRIMARY KEY,
            data_hash TEXT,
            size INTEGER,
            is_synced INTEGER,
            is_deleted INTEGER,
            added TEXT NOT NULL,
            seen TEXT NOT NULL
        )''')

def start() -> None:
    """
    Start a transaction
    """

    cursor = Context.instance.cursor()
    cursor.execute("BEGIN TRANSACTION")

def commit() -> None:
    """
    Commit a transaction
    """

    cursor = Context.instance.cursor()
    cursor.execute("COMMIT")

def record_get(record:FileRecord) -> FileRecord:
    """
    """
    
    cursor = Context.instance.cursor()

    query = "SELECT filename, data_hash, size, is_synced, is_deleted, added FROM records WHERE filename=? AND data_hash=?"

    cursor.execute(query, (record.filename, record.data_hash))
    row = cursor.fetchone()
    if not row:
        return
    
    filename, data_hash, size, is_synced, is_deleted, added = row

    return FileRecord.make(
        filename=filename,
        data_hash=data_hash,
        size=size,
        added=added,
        is_synced=bool(is_synced),
        is_deleted=bool(is_deleted),
    )

def record_touch(record:FileRecord) -> bool:
    L = "db.record_touch"
    cursor = Context.instance.cursor()
    now = helpers.now()

    cursor.execute("""
UPDATE records SET seen = ? WHERE filename = ?""", (
        now,
        record.filename,
    ))                     
    logger.debug(f"{L}: skipping {record.filename=}")
    return False

def record_put(record:FileRecord) -> bool:
    """
    NEED TO MAKE THIS MULTIPLE CALLS BECAUSE OF added
    """
    L = "db.record_put"

    cursor = Context.instance.cursor()
    now = helpers.now()

    cursor.execute("""
INSERT OR REPLACE INTO records (filename, data_hash, size, is_synced, is_deleted, seen, added) 
VALUES (?, ?, ?, ?, ?, ?, ?)""", (
        record.filename, 
        not record.is_deleted and record.data_hash or "", 
        not record.is_deleted and record.size or 0, 
        int(record.is_synced), 
        int(record.is_deleted),
        now,
        now,
    ))
    logger.debug(f"{L}: inserted/updated {record.filename=}")

def record_delete(record:FileRecord) -> bool:
    """
    """
    L = "db.record_put"

    cursor = Context.instance.cursor()
    now = helpers.now()

    cursor.execute("""
INSERT OR REPLACE INTO records (filename, data_hash, size, is_synced, is_deleted, seen, added) 
VALUES (?, ?, ?, ?, ?, ?, ?)""", (
        record.filename, 
        "", 
        0, 
        record.is_synced, 
        True,
        now,
        now,
    ))
    logger.debug(f"{L}: deleted {record.filename=}")

def list(is_synced:bool=None, is_deleted:bool=None, since_seen:str=None, since_added:str=None):
    """
    Return a list of records
    """
    
    cursor = Context.instance.cursor()

    query = "SELECT filename, data_hash, size, is_synced, is_deleted, added FROM records"
    params = []

    extras = []
    if is_synced is not None:
        extras.append("is_synced = ?")
        params.append(int(is_synced))

    if is_deleted is not None:
        extras.append("is_deleted = ?")
        params.append(int(is_deleted))

    if since_seen is not None:
        extras.append("seen >= ?")
        params.append(since_seen)

    if since_added is not None:
        extras.append("added >= ?")
        params.append(since_added)

    if extras:
        query += " WHERE " + " AND ".join(extras)

    # Execute the query and fetch the first record
    cursor.execute(query, params)
    while row := cursor.fetchone():
        filename, data_hash, size, is_synced, is_deleted, added = row

        yield FileRecord.make(
            filename=filename,
            data_hash=data_hash,
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
                UPDATE records SET is_deleted = ? WHERE seen < ? AND is_deleted = ?
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

