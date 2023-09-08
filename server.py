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

def get_authorized(authorization: HTTPAuthorizationCredentials = Security(security)):
    token_id = authorization.credentials
    authorized = bl.authorize(token_id)
    if authorized is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    ## add additional info here - IP address, etc.

    return authorized

@app.get("/docs/", tags=["secure"])
async def download(
    authorized: str = Depends(get_authorized),
):
    print("HERE:AUTHORIZED", authorized)
    try:
        return bl.pull_json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

@app.post("/docs/", tags=["secure"])
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None),
    authorized: str = Depends(get_authorized),
):
    print("HERE:AUTHORIZED", authorized)
    context = Context.instance

    match content_type:
        case "application/json":
            try:
                return bl.pushed_json(await request.json(), authorized=authorized)
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/zip":
            try:
                return bl.pushed_zip(await request.body(), authorized=authorized)
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

        case _:
            logger.error(f"Unsupported Content-Type header: {content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
