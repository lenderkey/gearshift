import os

from Context import Context
from structures import FileRecord, Token

import logging as logger

def authorization_header() -> dict:
    """
    Prepare HTTP header dict for Authorization 
    """

    return {
        "Authorization": "Bearer mysecrettoken",
    }

def authorize(token_id:str) -> Token:
    if token_id != "mysecrettoken":
        return
    
    return {
        "user": "admin",
    }