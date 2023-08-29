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
    data_hash: str
    size: int = 0
    is_synced: bool = False
    is_deleted: bool = False

    @classmethod
    def make(self, filename: str, **ad):
        return FileRecord(filename=filename, **ad)
    
    @classmethod
    def make_deleted(self, filename: str, **ad):
        return FileRecord(filename=filename, is_deleted=True)
    
    @property
    def path(self) -> str:
        from Context import Context

        return os.path.join(Context.instance.src_root, self.filename)

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
                    data_hash=helpers.sha256_file(fin),
                )
        except FileNotFoundError:
            logger.warning(f"{L}: file deleted {fullpath}")

            return FileRecord.make_deleted(
                filename=filename,
            )
        except IOError as x:
            logger.warning(f"{L}: cannot read {fullpath}: {x}")
