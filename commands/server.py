#
#   commands/server.py
#   
#   David Janes
#   Gearshift
#   2023-08-26
#

from Context import Context
from FileRecord import FileRecord

import logging as logger
import pprint

import click
import sys
import time
import subprocess

import helpers
import db

L = "server"

@cli.command("server", help="Run Gearshift Server") # type: ignore
def src_build():
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
    result = subprocess.run(command, capture_output=False, cwd="/Users/david/lenderkey/gearshift")
