from pydantic import BaseModel

class SyncItem(BaseModel):
    filename: str
    data_hash: str
    is_deleted: bool | None = None

class SyncItems(BaseModel):
    records: list[SyncItem] = list()
    more: bool | None = False
