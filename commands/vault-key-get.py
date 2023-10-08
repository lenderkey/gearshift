#
#   commands/vault-key-get.py
#   
#   David Janes
#   Gearshift
#   2023-09-30
#

from gearshift import Gearshift # type: ignore

import sys
import base64
import yaml
import click

import logging as logger

L = "vault-key-get"

@cli.command(L, help="") # type: ignore
@click.argument("--key-hash", default="current")
@click.option("--key-group", is_flag=False, default=None, help="Key Group (will use default otherwise)")
@click.option("--show-key", is_flag=True, default=False, help="output the key")
@click.option("--make-current", is_flag=True, default=False, help="make this key the current key")
def _(__key_hash:str=None, show_key:bool=False, make_current:bool=False, key_group:str=None):
    import hvac

    context = Gearshift.instance()
    key_root = context.get_vault_key_root()
    key_group = key_group or context.get_vault_key_group()
    vault_client = context.get_vault_client()
    key_path = f"{key_root}/{key_group}/{__key_hash}"
    try:
        read_response = vault_client.secrets.kv.v2.read_secret(
            path=key_path,
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
        key_path = f"{key_root}/{key_group}/current"

        vault_client.secrets.kv.v2.create_or_update_secret(
            path=key_path,
            secret={
                "key": key,
                "key_hash": key_hash,
            },
            mount_point='secret',
        )

        logger.info(f"{L}: key written to {key_path=}")

    if show_key:
        print(data['key'])
    else:
        print(yaml.safe_dump(data))

    # keys = list_response.get('data', {}).get('keys', [])
    # for key in keys:
    #     print(f"{key_root}.{key}")
