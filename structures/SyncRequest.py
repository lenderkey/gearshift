from pydantic import BaseModel

from .FileRecord import FileRecord

class SyncRequest(BaseModel):
    records: list[FileRecord] = list()
    more: bool | None = False
