from Context import Context
from structures import FileRecord
import helpers

import os

import logging as logger

def ingest_data(context:Context, item:FileRecord, data:bytes) -> bool:
    L = "Context.ingest_data"

    data_hash = helpers.sha256_data(data)
    assert data_hash == item.data_hash

    link_filename = context.dst_link_path(data_hash)

    if os.path.exists(link_filename):
        logger.info(f"{L}: {link_filename=} already exists - no need to write")
        return False
    
    os.makedirs(os.path.dirname(link_filename), exist_ok=True)

    try:
        link_filename_tmp = link_filename + ".tmp"
        with open(link_filename_tmp, "wb") as fout:
            fout.write(data)
    except IOError as x:
        logger.error(f"{L}: {x} writing {link_filename_tmp=}")

        try: os.remove(link_filename_tmp)
        except: pass

        raise x

    os.rename(link_filename_tmp, link_filename)
    logger.info(f"{L}: wrote {link_filename=}")

    return True

