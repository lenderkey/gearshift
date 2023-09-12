#
#   FileRecord.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

from typing import Optional

import os
import dataclasses
import datetime
import helpers

import logging as logger

@dataclasses.dataclass
class FileRecord:
    filename: str
    data_hash: str
    key_hash: str = ""
    aes_iv: Optional[bytes] = None
    aes_tag: Optional[bytes] = None
    size: int = 0
    is_synced: bool = False
    is_deleted: bool = False
    added: datetime.datetime = None

    @classmethod
    def make(self, filename: str, **ad) -> "FileRecord":
        obj = FileRecord(filename=filename, **ad)
        obj.cleanup()

        return obj
    
    @classmethod
    def make_deleted(self, filename: str, **ad) -> "FileRecord":
        obj = FileRecord(filename=filename, is_deleted=True)
        obj.cleanup()

        return obj

    def cleanup(self) -> None:
        ## total hack
        for key in [ "added", ]:
            value = getattr(self, key)
            if isinstance(value, str):
                setattr(self, key, helpers.to_datetime(value))

    @property
    def filepath(self) -> str:
        from Context import Context

        return os.path.join(Context.instance.src_root, self.filename)
    
    @property
    def linkpath(self) -> str:
        from Context import Context

        return Context.instance.dst_link_path(self.key_hash, self.data_hash)
    
    def to_dict(self, exclude:list=None) -> dict:
        d = dataclasses.asdict(self)

        if exclude is not None:
            for key in exclude:
                d.pop(key, None)

        return d

    def clone(self) -> "FileRecord":
        return FileRecord.make(**self.to_dict())

