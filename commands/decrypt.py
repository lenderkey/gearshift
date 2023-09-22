#
#   commands/decrypt.py
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

L = "decrypt"

import logging as logger

@cli.command("decrypt", help="decrypt a file") # type: ignore
@click.argument("input", default="-")
@click.option("--output", default="-", help="plaintext file")
def _(input:str, output:str):
    context = Context.instance

    if input == "-":
        plaintext = context.aes_decrypt_to_bytes(sys.stdin.buffer)
    else:
        plaintext = context.aes_decrypt_to_bytes(open(input, "rb"))

    if output == "-":
        sys.stdout.buffer.write(plaintext)
    else:
        with open(output, "wb") as fout:
            fout.write(plaintext)

    