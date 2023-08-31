import os

from Context import Context
from structures import FileRecord

import logging as logger

def record_delete(record:FileRecord):
    """
    """

    try:
        os.unlink(record.filepath)
    except FileNotFoundError:
        pass
