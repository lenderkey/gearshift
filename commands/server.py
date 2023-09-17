#
#   commands/server.py
#   
#   David Janes
#   Gearshift
#   2023-08-26
#

from Context import Context
from structures.FileRecord import FileRecord

import logging as logger
import pprint

import click
import sys
import time
import os
import subprocess

import helpers
import db

L = "server"

@cli.command("server", help="server: run the Gearshift server") # type: ignore
def _():
    """
    Example:
    ./gearshift server
    """

    context = Context.instance
    logger.info(f"{L}: started {context.src_root=}")
    # print("AAA", id(context), context.get("security.use_tokens"))

    command = [ 
        "uvicorn",
        "server:app",
        "--reload",
    ]
    result = subprocess.run(
        command, 
        capture_output=False, 
        cwd=os.path.dirname(__file__), env={
            **os.environ,
            "GEARSHIFT_CFG": context.cfg_file,
        },
    )
