from pydantic import BaseModel

from .FileRecord import FileRecord

class SyncItems(BaseModel):
    items: list[FileRecord] = list()
    more: bool | None = False
