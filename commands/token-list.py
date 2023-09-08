
#
#   commands/token-list.py
#   
#   David Janes
#   Gearshift
#   2023-09-08
#

from Context import Context

import yaml

L = "token-list"

@cli.command("token-list", help="") # type: ignore
def token_list():
    import db

    db.setup()

    for token in db.token_list():
        print(token)