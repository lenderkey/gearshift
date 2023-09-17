
#
#   commands/settings-put.py
#   
#   David Janes
#   Gearshift
#   2023-09-15
#

from Context import Context
import click

L = "settings-put"

@cli.command("settings-put", help="put a setting") # type: ignore
@click.argument("key", type=str)
@click.argument("value", type=str)
def _(key:str, value:str):
    import db

    db.setup()
    db.start()
    db.settings_put(key, value)
    db.commit()
