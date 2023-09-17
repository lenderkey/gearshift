#
#   commands/info.py
#   
#   David Janes
#   Gearshift
#   2023-03-30
#

from Context import Context

import yaml

L = "info"

@cli.command("info", help="tell me about this setup") # type: ignore
def _():
    context = Context.instance

    infod = {
        "doc_root": context.src_root,
        "server_url": context.src_url,
    }

    print(yaml.dump(infod))