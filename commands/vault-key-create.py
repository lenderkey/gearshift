#
#   commands/vault-key-create.py
#   
#   David Janes
#   Gearshift
#   2023-09-30
#

from Context import Context

import base64
import helpers
from Context import Context

import logging as logger

L = "vault-key-create"
PATH = 'aes0'

@cli.command(L, help="") # type: ignore
def _():
    from cryptography.fernet import Fernet

    context = Context.instance
    vault_client = context.get_vault_client()

    key:bytes = Fernet.generate_key()
    key_hash = helpers.sha256_data(key)
    key = base64.urlsafe_b64encode(key)
    key = key.decode("ascii")

    ## keep password
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=f"aes0/{key_hash}",
        secret={
            "key": key,
            "key_hash": key_hash,
        },
        mount_point='secret',
    )

    logger.info(f"{L}: key written to 'aes0/{key_hash}'")
