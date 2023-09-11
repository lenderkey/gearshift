import json
import os

from Context import Context
from structures import FileRecord, Token, Connection
import db

import logging as logger

def record_record(record:FileRecord, token:Token, connection:Connection, action:str):
    """
    """
    import bl
    import helpers
    ## print("HERE:record_record", action, os.path.split(record.filepath), token, connection)

    try:
        dir, filename = os.path.split(record.filepath)
        record_path = os.path.join(dir, ".records", filename)
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        with open(record_path, "a+") as fout:
            tokend = token.to_dict()
            del tokend["token_id"] ## not for you Jen

            json.dump({
                "action": action,
                "record": record.to_dict(),
                "token": tokend,
                "connection": connection.to_dict(),
            }, fout, default=helpers.default_serializer)
            fout.write("\n")

        logger.debug(f"record_record: {record.filename} in {record_path}")
    except IOError:
        logger.exception(f"record_record: {record.filepath}")
        raise
