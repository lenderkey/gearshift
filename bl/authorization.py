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

def authorize(token:str) -> dict:
    if token != "mysecrettoken":
        return
    
    return {
        "user": "admin",
    }