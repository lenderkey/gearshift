#
#   commands/encrypt.py
#   
#   David Janes
#   Gearshift
#   2023-08-06
#

import sys
import io

import click
import helpers

from Context import Context

L = "encrypt"

import logging as logger

@cli.command("encrypt", help="encrypt a file") # type: ignore
@click.argument("input", default="-")
@click.option("--output", default="-", help="crypttext file")
def _(input:str, output:str):
    context = Context.instance

    if input == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(input, "rb") as fin:
            data = fin.read()

    if output == "-":
        context.aes_encrypt_to_stream(key_hash=None, data=data, fout=sys.stdout.buffer)
    else:
        with open(output, "wb") as fout:
            context.aes_encrypt_to_stream(key_hash=None, data=data, fout=fout)

   