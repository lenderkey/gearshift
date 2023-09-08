import os
import sqlite3

from Context import Context
from structures import FileRecord, Token

import logging as logger

def authorization_header() -> dict:
    """
    Prepare HTTP header dict for Authorization 
    """

    return {
        "Authorization": "Bearer 12228912-1feb-4218-9532-cee4b65d1bd5",
    }

def authorize(token_id:str, connection:sqlite3.Connection=None) -> Token:
    """
    XXX - lean more into exceptions
    """
    import db

    print("HERE:XXX", token_id)
    token = db.token_by_id(token_id, connection=connection)
    print("HERE:YYY", token)
    if not token:
        return None

    if token.state != "A":
        return None

    return token
