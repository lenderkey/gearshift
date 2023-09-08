import uuid
import logging as logger
import datetime

from structures import Token

L = "token_create"

def token_create(email:str, path:str, expires:int, token_id:str=None):
    import db

    logger.info(f"{L}: {email=} {path=} {expires=}")

    token = Token(
        token_id=token_id or str(uuid.uuid4()),
        path=path,
        email=email,
        expires=datetime.datetime.now() + datetime.timedelta(days=expires),   
    )
    token = db.token_put(token)
    return token

    ## print(token)