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
            seen REAL NOT NULL
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

def get_record(filename:str) -> FileRecord:
    """
    """
    
    cursor = Context.instance.cursor()

    query = "SELECT filename, data_hash, size, is_synced, is_deleted FROM records WHERE filename=?"

    cursor.execute(query, (filename,))
    row = cursor.fetchone()
    if not row:
        return
    
    filename, data_hash, size, is_synced, is_deleted = row

    return FileRecord.make(
        filename=filename,
        data_hash=data_hash,
        size=size,
        is_synced=bool(is_synced),
        is_deleted=bool(is_deleted),
    )

def put_record(record:FileRecord, touch_only:bool=False):
    L = "db.put_record"

    cursor = Context.instance.cursor()
    seen_time = time.time()

    cursor.execute("SELECT data_hash FROM records WHERE filename=?", (record.filename,))
    row = cursor.fetchone()
    existing_data_hash = row and row[0]

    # If the record doesn't exist or the hashes don't exist, insert it
    if ( existing_data_hash is None or existing_data_hash != record.data_hash ):
        if touch_only:
            return 1
        
        cursor.execute("""
INSERT OR REPLACE INTO records (filename, data_hash, size, is_synced, is_deleted, seen) 
VALUES (?, ?, ?, ?, ?, ?)""", (
            record.filename, 
            record.data_hash, 
            record.size, 
            record.is_synced, 
            record.is_deleted,
            seen_time,
        ))
        logger.debug(f"{L}: inserted {record.filename=}")
        return 1
    else:
        cursor.execute("""
UPDATE records SET seen = ? WHERE filename = ?""", (
            seen_time,
            record.filename,
        ))                     
        logger.debug(f"{L}: skipping {record.filename=}")
        return 0

def list(is_synced:bool=None, is_deleted:bool=None):
    """
    Return a list of records
    """
    
    cursor = Context.instance.cursor()

    query = "SELECT filename, data_hash, size, is_synced, is_deleted FROM records"
    params = []

    extras = []
    if is_synced is not None:
        extras.append("is_synced = ?")
        params.append(int(is_synced))

    if is_deleted is not None:
        extras.append("is_deleted = ?")
        params.append(int(is_deleted))

    if extras:
        query += " WHERE " + " AND ".join(extras)

    # Execute the query and fetch the first record
    cursor.execute(query, params)
    while row := cursor.fetchone():
        filename, data_hash, size, is_synced, is_deleted = row

        yield FileRecord.make(
            filename=filename,
            data_hash=data_hash,
            size=size,
            is_synced=bool(is_synced),
            is_deleted=bool(is_deleted),
        )

def mark_deleted(cutoff:float, force:bool=False):
    """
    Mark a document as deleted if it has not been seen since the cutoff time.
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

