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
from FileRecord import FileRecord

import logging as logger

def setup() -> None:
    """
    Create a database table called records that looks like this:
    - filename
    - attr_hash
    - data_hash
    - is_synced
    - is_deleted

    If it already exists, do nothing.
    """

    cursor = Context.instance.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            filename TEXT PRIMARY KEY,
            size INTEGER,
            attr_hash TEXT,
            data_hash TEXT,
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
    Return a list of unsynced records
    """
    
    cursor = Context.instance.cursor()

    query = "SELECT filename, size, attr_hash, data_hash, is_synced, is_deleted FROM records WHERE filename=?"

    cursor.execute(query, (filename,))
    row = cursor.fetchone()
    if not row:
        return
    
    filename, size, attr_hash, data_hash, is_synced, is_deleted = row

    return FileRecord.make(
        filename=filename,
        size=size,
        attr_hash=attr_hash,
        data_hash=data_hash,
        is_synced=is_synced,
        is_deleted=is_deleted,
    )

def put_record(record:FileRecord):
    L = "db.put_record"

    cursor = Context.instance.cursor()
    seen_time = time.time()

    cursor.execute("SELECT attr_hash, data_hash FROM records WHERE filename=?", (record.filename,))
    row = cursor.fetchone()
    existing_attr_hash, existing_data_hash = row or ( None, None )

    # If the record doesn't exist or the hashes don't exist, insert it
    if ( existing_attr_hash is None or 
        existing_attr_hash != record.attr_hash or 
        existing_data_hash != record.data_hash 
    ):
        cursor.execute("""
INSERT OR REPLACE INTO records (filename, size, attr_hash, data_hash, is_synced, is_deleted, seen) 
VALUES (?, ?, ?, ?, ?, ?, ?)""", (
            record.filename, 
            record.size, 
            record.attr_hash, 
            record.data_hash, 
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

def unsynced():
    """
    Return a list of unsynced records
    """
    
    cursor = Context.instance.cursor()

    # Define the SQL query to retrieve unsynced records
    query = "SELECT filename, size, attr_hash, data_hash, is_synced, is_deleted FROM records WHERE is_synced = 0"

    # Execute the query and fetch the first record
    cursor.execute(query)
    while row := cursor.fetchone():
        filename, size, attr_hash, data_hash, is_synced, is_deleted = row

        yield FileRecord.make(
            filename=filename,
            size=size,
            attr_hash=attr_hash,
            data_hash=data_hash,
            is_synced=is_synced,
            is_deleted=is_deleted,
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

