#
#   commands/vault-key-view.py
#   
#   David Janes
#   Gearshift
#   2023-09-30
#

from Context import Context

import sys
import base64
import helpers
import yaml
import click
from Context import Context

import logging as logger

L = "vault-key-view"
PATH = 'aes0'

@cli.command(L, help="") # type: ignore
@click.argument("--key-hash", default="current")
@click.option("--show-key", is_flag=True, default=False, help="output the key")
@click.option("--make-current", is_flag=True, default=False, help="make this key the current key")
def _(__key_hash:str=None, show_key:bool=False, make_current:bool=False):
    import hvac

    context = Context.instance
    vault_client = context.get_vault_client()
    try:
        read_response = vault_client.secrets.kv.v2.read_secret(
            path=f'aes0/{__key_hash}',
        )
    except hvac.exceptions.InvalidPath:
        logger.error(f"{L}: key not found: {__key_hash}")
        sys.exit(1)

    data = read_response.get('data', {})
    data = data.get('data', {})
    key = data.get('key')
    key_hash = data.get('key_hash')

    if make_current:
        assert key
        assert key_hash

        vault_client.secrets.kv.v2.create_or_update_secret(
            path=f"aes0/current",
            secret={
                "key": key,
                "key_hash": key_hash,
            },
            mount_point='secret',
        )

        logger.info(f"{L}: key written to 'aes0/current'")

    if show_key:
        print(data['key'])
    else:
        print(yaml.safe_dump(data))

    # keys = list_response.get('data', {}).get('keys', [])
    # for key in keys:
    #     print(f"{PATH}.{key}")
