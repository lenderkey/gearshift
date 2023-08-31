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
    added: str = None

    @classmethod
    def make(self, filename: str, **ad):
        return FileRecord(filename=filename, **ad)
    
    @classmethod
    def make_deleted(self, filename: str, **ad):
        return FileRecord(filename=filename, is_deleted=True)
    
    @property
    def filepath(self) -> str:
        from Context import Context

        return os.path.join(Context.instance.src_root, self.filename)
    
    @property
    def linkpath(self) -> str:
        from Context import Context

        return Context.instance.dst_link_path(self.data_hash)
