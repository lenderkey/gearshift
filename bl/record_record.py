import os

from Context import Context
from structures import FileRecord
import db

import logging as logger

def record_record(record:FileRecord, authorized:dict, action:str):
    """
    """
    import bl
    print("HERE:record_record", action, os.path.split(record.filepath), authorized)