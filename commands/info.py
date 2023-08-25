#
#   commands/info.py
#   
#   David Janes
#   Gearshift
#   2023-03-30
#

from Context import Context

import yaml

L = "dst-zip"

@cli.command("info", help="tell me about this setup") # type: ignore
def dst_zip():
    context = Context.instance

    infod = {
        "source": {
            "root": context.src_root,
            "host": context.src_host,
            "user": context.src_user,
            "pem": context.src_pem,
        },
        "destination": {
            "root": context.dst_root,
            "links": context.dst_link_root,
        },
    }

    print(yaml.dump(infod))