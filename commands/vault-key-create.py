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
import click

import logging as logger

L = "vault-key-create"

@cli.command(L, help="") # type: ignore
@click.option("--key-group", is_flag=False, default=None, help="Key Group (will use default otherwise)")
def _(key_group:str=None):
    from cryptography.fernet import Fernet

    context = Context.instance
    key_root = context.get_vault_key_root()
    key_group = key_group or context.get_vault_key_group()
    vault_client = context.get_vault_client()

    key:bytes = Fernet.generate_key()
    key_hash = helpers.sha256_data(key)
    key = base64.urlsafe_b64encode(key)
    key = key.decode("ascii")

    ## keep password
    key_path = f"{key_root}/{key_group}/{key_hash}"
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=key_path,
        secret={
            "key": key,
            "key_hash": key_hash,
        },
        mount_point='secret',
    )

    logger.info(f"{L}: key written to {key_path=}")
