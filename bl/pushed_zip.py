import os
import zipfile
import io

from Context import Context
import bl

def pushed_zip(context:Context, raw_data:bytes) -> dict:
    raw_io = io.BytesIO(raw_data)

    zipper = zipfile.ZipFile(raw_io, mode="r")
    for dst_name in zipper.namelist():
        data = zipper.read(dst_name)
        in_item = bl.data_analyze(context, dst_name, data=data)
        is_written = bl.data_ingest(context, in_item, data=data)

        print("RECEIVED", in_item)

    return {"message": "Received Bytes", "length": len(raw_data)}
