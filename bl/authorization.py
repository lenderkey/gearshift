import os
import sqlite3
import datetime

from Context import Context
from structures import FileRecord, Token

import logging as logger

class TokenError(Exception):
    pass

class TokenExpired(TokenError):
    pass

class TokenNotFound(TokenError):
    pass

class TokenDeleted(TokenError):
    pass

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

    token = db.token_by_id(token_id, connection=connection)
    if not token:
        raise TokenNotFound()

    if token.state != "A":
        raise TokenDeleted()

    if token.expires < datetime.datetime.now():
        raise TokenExpired()

    return token
