import os
import zipfile
import io

from Context import Context
import bl
import db

def pushed_zip(raw_data:bytes) -> dict:
    print(raw_data)
    raw_io = io.BytesIO(raw_data)

    context = Context.instance
    db.setup()

    zipper = zipfile.ZipFile(raw_io, mode="r")
    for dst_name in zipper.namelist():
        data = zipper.read(dst_name)
        in_item = bl.data_analyze(dst_name, data=data)
        bl.data_ingest(in_item, data=data)

        db.start()
        db.record_put(in_item)
        db.commit()

        print("RECEIVED", in_item)

    return {"message": "Received Bytes", "length": len(raw_data)}
