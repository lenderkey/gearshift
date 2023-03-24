#
#   FileRecord.py
#
#   David Janes
#   Gearshift
#   2023-03-24
#
#   Database operations
#

import dataclasses

@dataclasses.dataclass
class FileRecord:
    filename: str
    name_hash: str
    attr_hash: str
    data_hash: str
    is_synced: bool = False
    is_deleted: bool = False

    @classmethod
    def make(self, filename: str, **ad):
        import helpers

        return FileRecord(filename=filename, name_hash=helpers.md5_data(filename), **ad)
    
    @classmethod
    def make_deleted(self, filename: str, **ad):
        import helpers
        
        return FileRecord(filename=filename, name_hash=helpers.md5_data(filename), is_deleted=True)
