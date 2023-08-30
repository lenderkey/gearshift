from fastapi import FastAPI, Request, Header, HTTPException

import os

from Context import Context
import db
import bl

app = FastAPI()

GEARSHIFT_CFG = os.environ["GEARSHIFT_CFG"]
Context.setup(cfg_file=GEARSHIFT_CFG)
db.setup()

@app.get("/docs/")
async def download():
    context = Context.instance

    try:
        return bl.pull_json(context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

@app.post("/docs/")
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None)
):
    context = Context.instance

    match content_type:
        case "application/json":
            try:
                return bl.pushed_json(context, await request.json())
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/zip":
            try:
                return bl.pushed_zip(context, await request.body())
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
