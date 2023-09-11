#
#   db/token.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

import sqlite3

from Context import Context
from structures import Token
import helpers

import logging as logger

def token_put(token:Token):
    """
    """
    L = "db.token_put"
    
    cursor = Context.instance.cursor()
    now = helpers.now()

    cursor.execute("""
INSERT OR REPLACE INTO tokens (id, token_id, path, state, email, data, added, seen, expires)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (   
        token.id,
        token.token_id,
        token.path,
        token.state,
        token.email,
        token.data,
        now,
        now,
        helpers.format_datetime(token.expires),
    ))
    logger.debug(f"{L}: inserted/updated {token.token_id=}")

    return token

def token_by_token_id(token_id:str, connection:sqlite3.Connection=None) -> Token:
    """
    """
    cursor = connection and connection.cursor() or Context.instance.cursor()

    query = "SELECT id, token_id, path, state, email, data, added, seen, expires FROM tokens WHERE token_id=?"
    params = [ token_id ]

    cursor.execute(query, params)
    row = cursor.fetchone()
    if not row:
        return
    
    id, token_id, path, state, email, data, added, seen, expires = row

    return Token.make(
        id=id,
        token_id=token_id,
        path=path,
        state=state,
        email=email,
        data=data,
        added=added,
        seen=seen,
        expires=expires,
    )

def token_list():
    query = "SELECT id, token_id, path, state, email, data, added, seen, expires FROM tokens"
    params = []

    cursor = Context.instance.cursor()

    cursor.execute(query, params)
    while row := cursor.fetchone():
        id, token_id, path, state, email, data, added, seen, expires = row
        yield Token.make(
            id=id,
            token_id=token_id,
            path=path,
            state=state,
            email=email,
            data=data,
            added=added,
            seen=seen,
            expires=expires,
        )


