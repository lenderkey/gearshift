#
#   gearshift.py
#
#   David Janes
#   Gearshift
#   2023-09-23
#   
#   Efficient File Transfer
#

import click
import os

import logging as logger

@click.group("cli", help="Gearshift Efficient File Transfer")
@click.pass_context
@click.option("--debug", is_flag=True)
@click.option("--cfg")
def cli(ctx, debug, cfg):
    import logging
    from Context import Context

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if cfg and cfg.find("/") == -1:
        if cfg.find(".") == -1:
            cfg += ".yaml"

        cfg = f"~/.gearshift/{cfg}"

    if cfg and cfg.find("~") == 0:
        cfg = os.path.expanduser(cfg)

    Context.setup(cfg_file=cfg)

if __name__ == '__main__':
    FOLDERS = [
        os.path.dirname(__file__)
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
