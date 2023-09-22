#
#   commands/key-create.py
#   
#   David Janes
#   Gearshift
#   2023-09-11
#

from Context import Context

import yaml
import click
import hashlib
import base64
import helpers
import os
import sys
from Context import Context

import logging as logger

L = "key-create"

@cli.command("key-create", help="server: generate a key and key_hash") # type: ignore
@click.option("--output", help="output file", default="~/.gearshift/keys/temporary.key")
@click.option("--force/--no-force", is_flag=True, default=False, help="overwrite existing keyfile")
def _(output:str, force:bool):
    from cryptography.fernet import Fernet

    context = Context.instance

    key:bytes = Fernet.generate_key()
    key_hash = helpers.sha256_data(key)

    output_filename = os.path.expanduser(output)

    if os.path.exists(output_filename) and not force:
        logger.fatal(f"{L}: {output_filename} already exists - remove, put aside or use --force")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "ab") as key_file:
        key_file.write(key)

    print(f"""\
Add (if needed) the following to {context.cfg_file}:

security:
  key_file: {output}
  key_hash: {key_hash}

If there is already a key_file, you can append the contents 
of the key_file to it.

You can give the key_file a better name if you prefer.
""")

    # cipher_suite = Fernet(key)
    # # Open file to encrypt
    # with open("file_to_encrypt.txt", "rb") as f:
    #     file_data = f.read()

    # # Encrypt data
    # encrypted_data = cipher_suite.encrypt(file_data)

    # # Write encrypted data to file
    # with open("file_to_encrypt.txt.encrypted", "wb") as f:
    #     f.write(encrypted_data)

