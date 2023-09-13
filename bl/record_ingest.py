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

    with lock:
        ## make the link file
        linkpath = record.linkpath
        
        if not os.path.exists(linkpath):
            logger.info(f"{L}: create {linkpath=}")
        
            os.makedirs(os.path.dirname(linkpath), exist_ok=True)

            if record.key_hash:
                key = Context.instance.server_key(record.key_hash)  
                aes_iv, aes_tag, aes_ciphertext = helpers.aes_encrypt(key, data)
            else:
                aes_iv, aes_tag, aes_ciphertext = None, None, data

            record = record.clone()

            try:
                link_filename_tmp = linkpath + ".tmp"
                with open(link_filename_tmp, "wb") as fout:
                    if not record.key_hash:
                        fout.write(bytes([ 0, 0 ]))
                        fout.write(aes_ciphertext)
                    else:
                        fout.write(bytes([ len(aes_iv) ]))
                        fout.write(aes_iv)
                        fout.write(bytes([ len(aes_tag) ]))
                        fout.write(aes_tag)

                    fout.write(aes_ciphertext)
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

    return record

