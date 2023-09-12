#
#   db/core.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

from Context import Context

import logging as logger

def setup() -> None:
    cursor = Context.instance.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            filename TEXT PRIMARY KEY,
            data_hash TEXT,
            key_hash TEXT NOT NULL DEFAULT "",
            aes_iv BLOB,
            aes_tag BLOB,
            size INTEGER,
            is_synced INTEGER,
            is_deleted INTEGER,
            added TEXT NOT NULL,
            seen TEXT NOT NULL
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_id TEXT UNIQUE, -- UUID
            path TEXT NOT NULL DEFAULT "/",
            state TEXT NOT NULL DEFAULT "A", -- "A": active, "D": deleted
            email TEXT NOT NULL, -- account which owns token
            data TEXT NOT NULL DEFAULT "{}", -- json data
            added TEXT NOT NULL, -- isodatetime
            seen TEXT NOT NULL, -- isodatetime
            expires TEXT NOT NULL -- isodatetime
    )''')
 
depth = 0

def start() -> None:
    """
    Start a transaction
    """
    global depth

    cursor = Context.instance.cursor()
    if depth == 0:
        cursor.execute("BEGIN TRANSACTION")
        depth += 1

def commit() -> None:
    """
    Commit a transaction
    """
    global depth

    cursor = Context.instance.cursor()

    depth -= 1
    if depth < 0:
        logger.error("db.commit: depth < 0")
        depth = 0
    elif depth == 0:
        cursor.execute("COMMIT")
        cursor.connection.commit()

def rollback() -> None:
    """
    Rollback a transaction
    """
    global depth

    cursor = Context.instance.cursor()
    cursor.connection.rollback()