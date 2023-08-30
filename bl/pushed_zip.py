import os
import zipfile
import io

from Context import Context
import bl
import db

def pushed_zip(context:Context, raw_data:bytes) -> dict:
    raw_io = io.BytesIO(raw_data)

    db.setup()

    zipper = zipfile.ZipFile(raw_io, mode="r")
    for dst_name in zipper.namelist():
        data = zipper.read(dst_name)
        in_item = bl.data_analyze(context, dst_name, data=data)
        bl.data_ingest(context, in_item, data=data)

        db.start()
        db.put_record(in_item)
        db.commit()

        print("RECEIVED", in_item)

    return {"message": "Received Bytes", "length": len(raw_data)}
