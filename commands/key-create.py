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

L = "key-create"

@cli.command("key-create", help="") # type: ignore
def _():
    from cryptography.fernet import Fernet

    key:bytes = Fernet.generate_key()
    keyhash = helpers.sha256_data(key)

    with open("gearshift.key", "wb") as key_file:
        key_file.write(key)

    print(keyhash)

    # cipher_suite = Fernet(key)
    # # Open file to encrypt
    # with open("file_to_encrypt.txt", "rb") as f:
    #     file_data = f.read()

    # # Encrypt data
    # encrypted_data = cipher_suite.encrypt(file_data)

    # # Write encrypted data to file
    # with open("file_to_encrypt.txt.encrypted", "wb") as f:
    #     f.write(encrypted_data)

