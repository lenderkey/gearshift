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

@cli.command("server", help="Run Gearshift Server") # type: ignore
def server():
    """
    Example:
    ./gearshift server
    """

    context = Context.instance
    logger.info(f"{L}: started {context.src_root=}")

    command = [ 
        "uvicorn",
        "server:app",
        "--reload",
    ]
    result = subprocess.run(command, capture_output=False, cwd="/Users/david/lenderkey/gearshift", env={
        **os.environ,
        "GEARSHIFT_CFG": context.cfg_file,
    })
