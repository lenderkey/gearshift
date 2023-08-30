from fastapi import FastAPI, Request, Header, HTTPException
import pprint

app = FastAPI()

from fastapi import FastAPI
from structures import SyncItems

import os
import zipfile
import io

from Context import Context
import db
import bl

GEARSHIFT_CFG = os.environ["GEARSHIFT_CFG"]
Context.setup(cfg_file=GEARSHIFT_CFG)
db.setup()

@app.post("/docs/")
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None)
):
    context = Context.instance

    match content_type:
        case "application/json":
            json_payload = await request.json()
            try:
                out_sync_items = SyncItems()
                in_sync_items = SyncItems(**json_payload)
                for item in in_sync_items.items:
                    if not db.put_record(item, touch_only=True):
                        continue

                    out_sync_items.items.append(item)
                    print("WANT", item)

                ## print("out_sync_items", out_sync_items)
                return out_sync_items
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/zip":
            raw_data = await request.body()
            raw_io = io.BytesIO(raw_data)

            zipper = zipfile.ZipFile(raw_io, mode="r")
            for dst_name in zipper.namelist():
                data = zipper.read(dst_name)
                in_item = bl.data_analyze(context, dst_name, data=data)
                is_written = bl.data_ingest(context, in_item, data=data)

                print("RECEIVED", in_item)

            return {"message": "Received Bytes", "length": len(raw_data)}

        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
