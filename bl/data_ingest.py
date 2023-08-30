from Context import Context
from structures import FileRecord
import helpers

import os
import threading

import logging as logger

lock = threading.Lock()

def data_ingest(context:Context, item:FileRecord, data:bytes) -> None:
    """
    This will create a link file (based on hash), and then link the destination
    file to the link file.

    Note that this is only used Server / Destination side. 
    """
    L = "Context.data_ingest"

    data_hash = helpers.sha256_data(data)
    assert data_hash == item.data_hash

    with lock:
        ## make the link file
        link_filename = context.dst_link_path(data_hash)
        
        if not os.path.exists(link_filename):
            logger.info(f"{L}: {link_filename=} already exists - no need to write")
        
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
        
        ## link the dst file - we could check inodes, but this is easier (?)
        dst_filename = item.filepath

        os.makedirs(os.path.dirname(dst_filename), exist_ok=True)

        try: os.unlink(dst_filename)
        except FileNotFoundError: pass

        os.link(link_filename, dst_filename)

