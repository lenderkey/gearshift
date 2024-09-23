import os

import logging as logger

def gearshift(filename:str, remove_on_write:bool=False) -> str:
    """
    If filename exists and filename.gear does not (or is older), create filename.gear.
    """
    from .io import Gearshift

    L = "ensure.gearshift"

    if filename.endswith(".gear"):
        filename = filename[:-5]

    gearname = filename + ".gear"

    ## filename must exist
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{L}: No such file: {filename}")

    gearname = filename + ".gear"

    with open(filename, "rb") as fin, Gearshift(gearname, mode="wb", remove_on_write=remove_on_write) as fout:
        fout.write(fin.read())

    logger.info(f"{L}: created {gearname}")
    return gearname

def filename(filename:str) -> str:
    """
    Make sure the orginal filename exists.
    """
    from .io import Gearshift

    L = "ensure.filename"

    if filename.endswith(".gear"):
        filename = filename[:-5]

    if os.path.exists(filename):
        return filename

    gearname = filename + ".gear"

    if not os.path.exists(gearname):
        raise FileNotFoundError(f"{L}: No such file: {gearname}")
    
    with Gearshift(gearname, mode="rb") as fin, open(filename, "wb") as fout:
        fout.write(fin.read())

    logger.info(f"{L}: created {filename}")
    return filename