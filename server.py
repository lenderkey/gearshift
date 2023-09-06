from fastapi import FastAPI, Request, Header, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


import os

from Context import Context
import db
import bl

app = FastAPI()

GEARSHIFT_CFG = os.environ["GEARSHIFT_CFG"]
Context.setup(cfg_file=GEARSHIFT_CFG)
db.setup()

import logging as logger

security = HTTPBearer()

def get_current_user(authorization: HTTPAuthorizationCredentials = Security(security)):
    token = authorization.credentials
    authorized = bl.authorize(token)
    if authorized is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return authorized

@app.get("/docs/", tags=["secure"])
async def download(
    authorized: str = Depends(get_current_user),
):
    print("HERE:XXX", authorized)
    try:
        return bl.pull_json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

@app.post("/docs/", tags=["secure"])
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None),
    authorized: str = Depends(get_current_user),
):
    context = Context.instance
    print("HERE:XXX", authorized)

    match content_type:
        case "application/json":
            try:
                return bl.pushed_json(await request.json())
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/ip":
            try:
                return bl.pushed_zip(await request.body())
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

        case _:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
