#
#   db.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

from Context import Context
from FileRecord import FileRecord

import logging as logger

def setup() -> None:
    """
    Create a database table called records that looks like this:
    - filename
    - name_hash
    - attr_hash
    - data_hash
    - is_synced
    - is_deleted

    If it already exists, do nothing.
    """

    cursor = Context.instance.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS records
                (filename TEXT,
                name_hash TEXT PRIMARY KEY,
                attr_hash TEXT,
                data_hash TEXT,
                is_synced INTEGER,
                is_deleted INTEGER)''')

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

def put_record(record:FileRecord):
    L = "db.put_record"
    cursor = Context.instance.cursor()

    # Check if a record with the same name_hash already exists
    cursor.execute("SELECT attr_hash FROM records WHERE name_hash=?", (record.name_hash,))
    existing_attr_hash = cursor.fetchone()

    # If the record doesn't exist or the attr_hash has changed, insert the new record
    if existing_attr_hash is None or existing_attr_hash[0] != record.attr_hash:
        cursor.execute("""
INSERT OR REPLACE INTO records (filename, name_hash, attr_hash, data_hash, is_synced, is_deleted) 
VALUES (?, ?, ?, ?, ?, ?)""", (
            record.filename, 
            record.name_hash, 
            record.attr_hash, 
            record.data_hash, 
            record.is_synced, 
            record.is_deleted,
        ))
        logger.debug(f"{L}: inserted {record.filename=}")
        return 1
    else:
        logger.debug(f"{L}: skipping {record.filename=}")
        return 0
