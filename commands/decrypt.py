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

from gearshift import Gearshift # type: ignore

L = "decrypt"

import logging as logger

@cli.command("decrypt", help="decrypt a file") # type: ignore
@click.argument("input", default="-")
@click.option("--output", default="-", help="plaintext file")
def _(input:str, output:str):
    from gearshift import AES0File

    context = Gearshift.instance()

    if input == "-":
        plaintext = context.aes_decrypt_to_bytes(sys.stdin.buffer)
    else:
        with AES0File(input, "rb") as fin:
            plaintext = fin.read()

    if output == "-":
        sys.stdout.buffer.write(plaintext)
    else:
        with open(output, "wb") as fout:
            fout.write(plaintext)

    