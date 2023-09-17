
#
#   commands/settings.py
#   
#   David Janes
#   Gearshift
#   2023-09-15
#

from Context import Context

L = "settings"

@cli.command("settings", help="show settings") # type: ignore
def _():
    import db

    db.setup()
    print(db.settings())
