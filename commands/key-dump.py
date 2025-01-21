#
#   commands/dump.py
#   
#   David
#   Gearshift
#   2023-12-07
#

import sys

import click
import base64
import json

from gearshift.context import GearshiftContext
from gearshift.helpers import sha256_data

L = "key-dump"

@cli.command(L, help="dump keys as JSON -- good for AWS secrets") # type: ignore
@click.argument("keyfile")
def _(keyfile:str):
    context = GearshiftContext.instance(cfg_optional=True)

    d = {}
    with open(keyfile, "rb") as fin:
        for key in fin.read().split(b"\n"):
            d[sha256_data(key)] = base64.urlsafe_b64encode(key).decode("utf-8")

    json.dump(d, sys.stdout, indent=2)
    print()