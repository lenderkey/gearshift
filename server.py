from fastapi import FastAPI, Request, Header, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os
import asyncio
import sqlite3

from Context import Context
from structures import Token

import db
import bl

app = FastAPI()

server_connection = None

async def run_in_threadpool(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)

GEARSHIFT_CFG = os.environ["GEARSHIFT_CFG"]
Context.setup(cfg_file=GEARSHIFT_CFG)
db.setup()

import logging as logger

security = HTTPBearer()

async def get_authorized(authorization: HTTPAuthorizationCredentials = Security(security)):
    def execute_query():
        global server_connection

        if not server_connection:
            server_connection = sqlite3.connect(Context.instance.db_path)

        token_id = authorization.credentials
        try:
            token = bl.authorize(token_id, connection=server_connection)
        except bl.TokenError:
            logger.exception(f"token error: {token_id=}")

            raise HTTPException(status_code=401, detail="Invalid token")

        return token

    return await run_in_threadpool(execute_query)

@app.get("/docs/", tags=["secure"])
async def download(
    token: str = Depends(get_authorized),
):
    print("HERE:AUTHORIZED", token)
    try:
        return bl.pull_json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

@app.post("/docs/", tags=["secure"])
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None),
    token: str = Depends(get_authorized),
):
    print("HERE:AUTHORIZED", token)
    context = Context.instance

    match content_type:
        case "application/json":
            try:
                return bl.pushed_json(await request.json(), token=token)
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/zip":
            try:
                return bl.pushed_zip(await request.body(), token=token)
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

        case _:
            logger.error(f"Unsupported Content-Type header: {content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
