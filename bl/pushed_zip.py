import zipfile
import io

from Context import Context
from structures import SyncRequest, Token, Connection
import bl
import db

def pushed_zip(raw_data:bytes, token:Token, connection:Connection) -> dict:
    """
    SERVER side when the CLIENT sends a ZIP with documents
    """
    zipper = zipfile.ZipFile(io.BytesIO(raw_data), mode="r")
    for dst_name in zipper.namelist():
        data = zipper.read(dst_name)
        record = bl.data_analyze(dst_name, data=data)

        bl.record_put(record, data=data, token=token, connection=connection)

    ## placeholder message
    return {"message": "Received Bytes", "length": len(raw_data)}
