from fastapi import FastAPI, Request, Header, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os
import asyncio
import sqlite3

from Context import Context
from structures import Token, Connection

import db
import bl

import logging as logger
logger.basicConfig(level=logger.DEBUG)


app = FastAPI()

server_connection = None

async def run_in_threadpool(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)

GEARSHIFT_CFG = os.environ["GEARSHIFT_CFG"]
Context.setup(cfg_file=GEARSHIFT_CFG)
db.setup()

security = HTTPBearer()

async def get_authorized(authorization: HTTPAuthorizationCredentials = Security(security)) -> Token:
    """
    If you set security.use_tokens to False, then this will always return the same token
    and basically as long as you pass anything for "Authentication: Bearer" you'll be
    authorized. Needless to say, this is for testing only.
    """
    def execute_query():
        global server_connection

        if not server_connection:
            server_connection = sqlite3.connect(Context.instance.db_path)

        if not Context.instance.get("security.use_tokens", default=True):
            return Token(token_id="no-token", email="no-user", path="/")

        token_id = authorization.credentials
        try:
            token = bl.authorize(token_id, connection=server_connection)
        except bl.TokenError:
            logger.exception(f"token error: {token_id=}")

            raise HTTPException(status_code=401, detail="Invalid token")

        return token

    return await run_in_threadpool(execute_query)

@app.get("/", tags=["secure"])
async def download(
    request: Request,
    token: Token = Depends(get_authorized),
):
    connection = Connection.from_request(request)

    try:
        return bl.pull_json(connection=connection, 
            since_added=request.query_params.get("added"),
            limit=int(request.query_params.get("limit") or "0"),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

@app.post("/", tags=["secure"])
async def upload_bytes_or_json(
    request: Request,
    content_type: str = Header(None),
    token: Token = Depends(get_authorized),
):
    import db

    # print("HERE:AUTHORIZED", token)
    context = Context.instance
    connection = Connection.from_request(request)

    db.setup()
    match content_type:
        case "application/json":
            try:
                return bl.pushed_json(await request.json(), token=token, connection=connection)\
                    .model_dump(mode="json", exclude=["aes_iv", "aes_tag", "key_hash", "seen"])
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/zip":
            try:
                return bl.pushed_zip(await request.body(), token=token, connection=connection)
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

        case _:
            logger.error(f"Unsupported Content-Type header: {content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Content-Type header: {content_type}",
            )
