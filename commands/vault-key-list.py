#
#   commands/vault-key-list.py
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

L = "vault-key-list"
PATH = 'aes0'

@cli.command(L, help="") # type: ignore
def _():
    from cryptography.fernet import Fernet

    context = Context.instance
    vault_client = context.get_vault_client()

    list_response = vault_client.secrets.kv.v2.list_secrets(
        path=PATH,
    )

    keys = list_response.get('data', {}).get('keys', [])
    for key in keys:
        print(f"{key}")
