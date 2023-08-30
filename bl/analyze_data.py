import os

from Context import Context
from structures import FileRecord

import logging as logger

def analyze_data(context:Context, filename:str, data:bytes) -> FileRecord:
    """
    Make a FileRecord for a file where we just have the bytes.
    """
    L = "bl.analyze_data"

    import helpers
    
    return FileRecord.make(
        filename=filename,
        size=len(data),
        data_hash=helpers.sha256_data(data),
    )
