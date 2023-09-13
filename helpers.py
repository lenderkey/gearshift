#
#   helpers.py
#
#   David Janes
#   Gearshift
#   2023-03-23
#

from typing import BinaryIO, Union, Any, Tuple

import re
import hashlib
import os
import base64
import datetime

from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.backends import default_backend

import logging as logger

def _list_advance(o, keypath:str, required:bool, key:str=None) -> Any:
    while isinstance(o, list):
        if len(o) == 0 and required:
            raise KeyError(keypath)
        elif len(o) == 0:
            o = o[0]
        else:
            break

    return o

def set(d:dict, keypath:str, value:object) -> None:
    parts = keypath.split(".")
    for key in parts[:-1]:
        ## d = _list_advance(d, keypath, required=False, key=key)
        nextd = d.get(key)
        if nextd is None:
            nextd = d[key] = {}

        d = nextd

    key = parts[-1]
    d[key] = value

def get(d:dict, keypath:str, default:Any=None, required:bool=False, first:bool=True) -> Any:
    assert isinstance(required, bool)

    parts = keypath.split(".")
    for key in parts[:-1]:
        d = _list_advance(d, keypath, required, key=key)

        if required and key not in d:
            raise KeyError(keypath)

        d = d.get(key, {})

    key = parts[-1]
    d = _list_advance(d, keypath, required, key=key)
    if d is not None and key in d:
        value = d[key]

        if isinstance(value, list) and first:
            if not value:
                if required:
                    raise KeyError(keypath)
                else:
                    return default
            else:
                value = value[0]

        return value
    elif required:
        raise KeyError(keypath)
    else:
        return default


def sha256_file(fd:BinaryIO) -> str:
    sha256 = hashlib.sha256()
    while True:
        data = fd.read(65536)  # Read 64KB at a time
        if not data:
            break
        sha256.update(data)

    return base64.urlsafe_b64encode(sha256.digest()).decode("utf-8").rstrip("=")

def sha256_data(*av) -> str:
    hasher = hashlib.sha256()
    for x, data in enumerate(av):
        if x:
            hasher.update(b"@@")

        if not isinstance(data, bytes):
            data = str(data).encode("utf-8")
            
        hasher.update(data)

    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8").rstrip("=")

def md5_data(*av) -> str:
    hasher = hashlib.md5()
    for x, data in enumerate(av):
        if x:
            hasher.update(b"@@")

        if not isinstance(data, bytes):
            data = str(data).encode("utf-8")

        hasher.update(data)

    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8").rstrip("=")

def walker():
    from Context import Context

    root = Context.instance.src_root
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files[:] = [d for d in files if not d.startswith('.')]

        for filename in files:
            if filename.startswith("."):
                continue

            filename = os.path.join(folder, filename)
            filename = os.path.relpath(filename, root)

            yield filename

def now() -> str:
    return format_datetime(datetime.datetime.utcnow())

def format_datetime(dt:str|datetime.datetime|None) -> str|None:
    if dt is None:
        return None
    elif isinstance(dt, datetime.datetime):
        return dt.isoformat()
    elif isinstance(dt, str):
        return dt
    else:
        raise TypeError(f"expected datetime or str, not {type(dt)}")

def to_datetime(dt:str|datetime.datetime|None) -> datetime.datetime|None:
    if dt is None:
        return None
    elif isinstance(dt, str):
        return datetime.datetime.fromisoformat(dt)
    elif isinstance(dt, datetime.datetime):
        return dt
    else:
        raise TypeError(f"expected datetime or str, not {type(dt)}")

def default_serializer(o):
    if isinstance(o, datetime.datetime):
        return format_datetime(o)
    
    raise TypeError("Object of type datetime is not JSON serializable")

def aes_key(key:bytes) -> bytes:
    return base64.urlsafe_b64decode(key)
    return key
    ## XXX - cache me?
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

    salt = b'm\xd5J\x9c\r\x88\xbf|\xeeN\xb1)\x87\xe82\t'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = key[:32]

    print("HERE:XXX", key, len(key))    
    return key

def aes_encrypt(key:bytes, data:bytes, iv:bytes) -> Tuple[bytes, bytes, bytes]:
    iv = os.urandom(12)
    encryptor = ciphers.Cipher(
        ciphers.algorithms.AES(key),
        ciphers.modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return (iv, encryptor.tag, ciphertext)

def aes_decrypt(key:bytes, iv:bytes, tag:bytes, ciphertext:bytes) -> bytes:
    decryptor = ciphers.Cipher(
        ciphers.algorithms.AES(key),
        ciphers.modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

if __name__ == '__main__':
    import pprint
    value = os.urandom(12)
    value = base64.urlsafe_b64encode(value)
    value = value.decode("ascii")
    base64.urlsafe_b64decode(value)
    pprint.pprint(value)