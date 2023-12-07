#
#   commands/key-create.py
#   
#   David Janes
#   Gearshift
#   2023-09-11
#

import click
import os
import sys

import logging as logger

L = "key-create"

@cli.command(L, help="server: generate a key and key_hash") # type: ignore
@click.option("--output", help="output file", default="~/.gearshift/keys/temporary.key")
@click.option("--force/--no-force", is_flag=True, default=False, help="overwrite existing keyfile")
def _(output:str, force:bool):
    from cryptography.fernet import Fernet
    from gearshift import helpers
    from gearshift.context import GearshiftContext

    context = GearshiftContext.instance

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
Add (if needed) the following to gearshift.yaml:

security:
  key_file: {output}
  key_hash: {key_hash}

If there is already a key_file, you can append the contents 
of the key_file to it.

You can give the key_file a better name if you prefer.
""")
