#
#   gearshift.py
#
#   David
#   Gearshift
#   2023-09-23
#   
#   Encryption at Rest
#

import click
import os
import json

import logging as logger

@click.group("cli", help="Gearshift - Encryption at Rest")
@click.pass_context
@click.option("--debug", is_flag=True)
@click.option("--set", "set_", multiple=True, help="change configuration after it is loaded")
@click.option("--cfg")
def cli(ctx, debug, cfg, set_):
    import logging
    from gearshift.context import GearshiftContext

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg_file = None
    if cfg:
        cfg_file = cfg
        if cfg_file.find("/") == -1:
            if cfg_file.find(".") == -1:
                ccfg_filefg += ".yaml"

            cfg_file = f"~/.gearshift/{cfg}"

        if cfg_file.find("~") == 0:
            cfg_file = os.path.expanduser(cfg_file)

    context = GearshiftContext.instance(cfg_file=cfg_file, cfg_optional=not cfg)

    updates = {}
    for kv in set_:
        k, v = kv.split("=")
        try: 
            v = int(v)
        except ValueError:
            pass

        updates[k] = v
        context.set(k, v)

    os.environ["GEARSHIFT_SET"] = json.dumps(updates)

if __name__ == '__main__':
    FOLDERS = [
        os.path.join(os.path.dirname(__file__), ".."),
    ]

    for FOLDER in FOLDERS:
        COMMANDS = os.path.join(FOLDER, "commands")
        if not os.path.isdir(COMMANDS):
            continue

        files = os.listdir(COMMANDS)
        files.sort()
        files = filter(lambda name: name != "__init__.py", files)
        files = filter(lambda name: name[:1] != ".", files)
        files = filter(lambda name: name.endswith(".py"), files)
        files = map(lambda name: os.path.join(COMMANDS, name), files)
        files = list(files)

        for file in files:
            with open(file) as fin:
                code = compile(fin.read(), file, 'exec')
                code = eval(code)

    cli(prog_name="gearshift")
