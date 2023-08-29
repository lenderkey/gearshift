#
#   FileRecord.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

import os
import dataclasses

import logging as logger

@dataclasses.dataclass
class FileRecord:
    filename: str
    attr_hash: str
    data_hash: str
    size: int
    is_synced: bool = False
    is_deleted: bool = False

    @classmethod
    def make(self, filename: str, **ad):
        import helpers

        return FileRecord(filename=filename, **ad)
    
    @classmethod
    def make_deleted(self, filename: str, **ad):
        import helpers
        
        return FileRecord(filename=filename, is_deleted=True)

    def analyze(filename:str) -> dict:
        L = "helpers.analyze"

        from Context import Context
        import helpers
        
        fullpath = os.path.join(Context.instance.src_root, filename)
        stbuf = os.stat(fullpath)

        try:
            with open(fullpath, "rb") as fin:
                return FileRecord.make(
                    filename=filename,
                    size=stbuf.st_size,
                    attr_hash=helpers.md5_data(stbuf.st_ino, stbuf.st_size, stbuf.st_mtime),
                    data_hash=helpers.sha256_file(fin),
                )
        except FileNotFoundError:
            logger.warning(f"{L}: file deleted {fullpath}")

            return FileRecord.make_deleted(
                filename=filename,
            )
        except IOError as x:
            logger.warning(f"{L}: cannot read {fullpath}: {x}")
