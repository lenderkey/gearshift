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
    action: str = "default",
):
    import db

    # print("HERE:AUTHORIZED", token)
    context = Context.instance
    connection = Connection.from_request(request)

    db.setup()
    match content_type, action:
        case "application/json", "default":
            try:
                return bl.pushed_json(await request.json(), token=token, connection=connection)\
                    .model_dump(mode="json", exclude=["aes_iv", "aes_tag", "key_hash", "seen"])
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/json", "get-zip":
            try:
                return bl.pushed_json(await request.json(), token=token, connection=connection)\
                    .model_dump(mode="json", exclude=["aes_iv", "aes_tag", "key_hash", "seen"])
            except Exception as e:
                logger.exception(f"unexpected error")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")
            
        case "application/zip", _:
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

@app.post("/{path}", tags=["secure"])
async def post_file(
    request: Request,
    path: str,
    content_type: str = Header(None),
    token: Token = Depends(get_authorized),
):
    return "Hello!"

@app.get("/{path:path}", tags=["secure"])
async def get_file(
    request: Request,
    path: str,
    token: Token = Depends(get_authorized),
):
    from structures import FileRecord
    record = FileRecord(filename=path, data_hash="")
    record = db.record_get(record, mode="filename")
    if not record:
        raise HTTPException(status_code=400, detail=f"File not found")
    if record.is_deleted:
        raise HTTPException(status_code=400, detail=f"File deleted")

    from fastapi.responses import StreamingResponse
    from io import BytesIO
    import mimetypes
    import helpers

    with open(record.linkpath, "rb") as fin:
        data = fin.read()
        key = Context.instance.server_key(record.key_hash)     
        print("KEY", key, type(key), record.key_hash)
        print(type(record.aes_iv), type(record.aes_tag), type(data))
        data = helpers.aes_decrypt(key, iv=record.aes_iv, tag=record.aes_tag, ciphertext=data)
        ## print("DATA", data)
    
    return StreamingResponse(BytesIO(data), media_type=mimetypes.guess_type(record.filename)[0])
    
    print(record)
    return f"Hello! {path=}"
