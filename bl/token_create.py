import uuid
import logging as logger
import datetime

from structures import Token

L = "token_create"

def token_create(email:str, path:str, expires:int):
    import db

    logger.info(f"{L}: {email=} {path=} {expires=}")

    token = Token(
        token=str(uuid.uuid4()),
        path=path,
        email=email,
        expires=datetime.datetime.now() + datetime.timedelta(days=expires),   
    )
    db.token_put(token)

    ## print(token)