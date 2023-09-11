from Context import Context
from structures import FileRecord
import helpers

import os
import threading

import logging as logger

lock = threading.Lock()

def record_ingest(record:FileRecord, data:bytes) -> None:
    """
    This will create a link file (based on hashES), and then link the destination
    file to the link file.

    Note that this is only used Server / Destination side. 
    """
    L = "bl.record_ingest"

    data_hash = helpers.sha256_data(data)
    assert data_hash == record.data_hash

    write_data = data

    if record.key_hash:
        from cryptography.fernet import Fernet
        cipher_suite = Fernet(Context.instance.server_key(record.key_hash))
        write_data = cipher_suite.encrypt(data)

    with lock:
        ## make the link file
        linkpath = record.linkpath
        
        if not os.path.exists(linkpath):
            logger.info(f"{L}: {linkpath=} already exists - no need to write")
        
            os.makedirs(os.path.dirname(linkpath), exist_ok=True)

            try:
                link_filename_tmp = linkpath + ".tmp"
                with open(link_filename_tmp, "wb") as fout:
                    fout.write(write_data)
            except IOError as x:
                logger.error(f"{L}: {x} writing {link_filename_tmp=}")

                try: os.remove(link_filename_tmp)
                except: pass

                raise x

            os.rename(link_filename_tmp, linkpath)
            logger.info(f"{L}: wrote {linkpath=}")
        
        ## link the dst file - we could check inodes, but this is easier (?)
        dst_filename = record.filepath

        os.makedirs(os.path.dirname(dst_filename), exist_ok=True)

        try: os.unlink(dst_filename)
        except FileNotFoundError: pass

        os.link(linkpath, dst_filename)

