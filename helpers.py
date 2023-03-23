#
#   helpers.py
#
#   David Janes
#   Gearshift
#   2023-03-23
#

from typing import Union, Any
import re

def _list_advance(o, keypath:str, required:bool, key=None):
    while isinstance(o, list):
        if len(o) == 0 and required:
            raise KeyError(keypath)
        elif len(o) == 0:
            o = o[0]
        else:
            break

    return o

def set(d, keypath:str, value:object):
    parts = keypath.split(".")
    for key in parts[:-1]:
        ## d = _list_advance(d, keypath, required=False, key=key)
        nextd = d.get(key)
        if nextd is None:
            nextd = d[key] = {}

        d = nextd

    key = parts[-1]
    d[key] = value

def get(d, keypath:str, default:Any=None, required:bool=False, first:bool=True) -> Any:
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
