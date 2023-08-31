import os

from Context import Context
from structures import FileRecord

import logging as logger

def file_analyze(filename:str) -> FileRecord:
    """
    Make a FileRecord for a file that already exists on disk.
    If it is not found, it makes a deleted record.
    """
    L = "bl.file_analyze"

    import helpers

    filepath = os.path.join(Context.instance.src_root, filename)
    stbuf = os.stat(filepath)

    try:
        with open(filepath, "rb") as fin:
            return FileRecord.make(
                filename=filename,
                size=stbuf.st_size,
                data_hash=helpers.sha256_file(fin),
            )
    except FileNotFoundError:
        logger.warning(f"{L}: file deleted {filepath}")

        return FileRecord.make_deleted(
            filename=filename,
        )
    except IOError as x:
        logger.warning(f"{L}: cannot read {filepath}: {x}")
