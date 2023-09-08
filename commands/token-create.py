#
#   commands/token-create.py
#   
#   David Janes
#   Gearshift
#   2023-09-08
#

from Context import Context

import yaml
import click

L = "token-create"

@cli.command("token-create", help="") # type: ignore
@click.option("--email", default=None, help="email address", required=True)
@click.option("--path", default="/", help="path")
@click.option("--expires", default=730, type=int, help="expires (in days from now)")
@click.option("--token-id", default=None, help="path")
def token_create(email:str, path:str, expires:int, token_id:str=None):
    import bl
    import db

    db.setup()
    db.start()
    
    token = bl.token_create(email=email, path=path, expires=expires, token_id=token_id)

    db.commit()

    print(token.token_id)
