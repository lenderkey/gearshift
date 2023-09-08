import os

from Context import Context
from structures import FileRecord

import logging as logger

def authorization_header() -> dict:
    """
    Prepare HTTP header dict for Authorization 
    """

    return {
        "Authorization": "Bearer mysecrettoken",
    }

def authorize(token_id:str) -> dict:
    if token_id != "mysecrettoken":
        return
    
    return {
        "user": "admin",
    }