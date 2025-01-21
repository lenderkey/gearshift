#
#   commands/vault-key-list.py
#   
#   David
#   Gearshift
#   2023-09-30
#

from gearshift.context import GearshiftContext

import sys
import click

import logging as logger

L = "vault-key-list"

@cli.command(L, help="") # type: ignore
@click.option("--key-group", is_flag=False, default=None, help="Key Group (will use default otherwise)")
def _(key_group:str=None):
    import hvac

    context = GearshiftContext.instance()
    key_root = context.get_vault_key_root()
    key_group = key_group or context.get_vault_key_group()
    vault_client = context.get_vault_client()

    key_path = f"{key_root}/{key_group}"
    try:
        list_response = vault_client.secrets.kv.v2.list_secrets(
            path=key_path,
        )

        keys = list_response.get('data', {}).get('keys', [])
        for key in keys:
            print(f"{key}")
    except hvac.exceptions.InvalidPath:
        logger.info(f"{L}: no keys!")
        sys.exit(0)
