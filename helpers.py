#
#   helpers.py
#
#   David Janes
#   Gearshift
#   2023-03-23
#

from typing import BinaryIO, Union, Any

import re
import hashlib
import os
import base64

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

def md5_data(*av) -> str:
    md5 = hashlib.md5()
    for item in av:
        data = str(item).encode("utf-8")
        md5.update(data)
        md5.update(b"@@")

    return base64.urlsafe_b64encode(md5.digest()).decode("utf-8").rstrip("=")

def walker():
    from Context import Context

    root = Context.instance.src_root_path
    for folder, dirs, files in os.walk(root):
        for filename in files:
            filename = os.path.join(folder, filename)
            filename = os.path.relpath(filename, root)

            yield filename

def analyze(filename:str) -> dict:
    L = "helpers.analyze"

    from Context import Context
    
    fullpath = os.path.join(Context.instance.src_root_path, filename)
    stbuf = os.stat(fullpath)

    try:
        with open(fullpath, "rb") as fin:
            """Make SHA256 hash of file context"""

            return {
                "filename": filename,
                "nhash": md5_data(filename),
                "ahash": md5_data(stbuf.st_ino, stbuf.st_size, stbuf.st_mtime),
                "fhash": sha256_file(fin),
            }
    except IOError:
        logger.warning(f"{L}: cannot open {fullpath}")

        return {
            "filename": filename,
            "nhash": md5_data(filename),
            "ahash": None,
            "fhash": None,
        }
