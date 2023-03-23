#
#   commands/build.py
#   
#   David Janes
#   Gearshift
#   2023-09-23
#

from Context import Context

import hashlib
import os
import logging as logger
import pprint

import click

L = "build"


def sha256_file(fd):
    sha256 = hashlib.sha256()
    while True:
        data = fd.read(65536)  # Read 64KB at a time
        if not data:
            break
        sha256.update(data)

    return sha256.hexdigest()

def md5_data(*av):
    md5 = hashlib.md5()
    for item in av:
        data = str(item).encode("utf-8")
        md5.update(data)
        md5.update(b"@@")
    return md5.hexdigest()

def walker():
    root = Context.instance.src_root_path
    for folder, dirs, files in os.walk(root):
        for filename in files:
            filename = os.path.join(folder, filename)
            filename = os.path.relpath(filename, root)

            yield filename

def analyze(filename):
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

@cli.command("build", help="Build a Gearshift Database") # type: ignore
@click.option("--quit-on-error/--no-quit-on-error", is_flag=True)
@click.option("--csv", help="use CSV logger to this file")
def build(quit_on_error, csv):
    context = Context.instance
    logger.info(f"{L}: started {context.src_root_path=}")

    cursor = context.cursor()

    for filename in walker():
        pprint.pprint(analyze(filename))