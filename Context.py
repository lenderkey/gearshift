#
#   Context.py
#
#   David Janes
#   Gearshift
#   2023-03-23
#

from collections.abc import Callable

import yaml
import os

import logging as logger

class Context:
    instance = None

    def __init__(self, cfg_file=None):
        L = "__init__"

        self.cfg_file = cfg_file or os.path.expanduser("~/.gearshift/gearshift.yaml")
        self.cfg_folder = os.path.abspath(os.path.dirname(self.cfg_file))
        self.cfg = {}

        try:
            with open(self.cfg_file) as fin:
                self.cfg = yaml.safe_load(fin) or self.cfg
        except IOError:
            logger.warning(f"{L}: {self.cfg_file=} not found")
            pass

        logger.debug(f"{L}: {self.cfg_file=}")

    @classmethod
    def setup(self, **ad):
        if not Context.instance:
            Context.instance = Context(**ad)

    def get(self, keypath:str, default:bool=None, required=False):
        return helpers.get(self.cfg, keypath, default=default, required=required)

    def resolve_path(self, path:str):
        if path.startswith("~"):
            return os.path.normpath(os.path.expandpath(path))
        elif path.startswith("./"):
            return os.path.normpath(os.path.join(self.cfg_folder, path))
        else:
            return path

if __name__ == '__main__':
    context = Context()
    print(context.db)
