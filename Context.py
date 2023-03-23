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
import sys
import sqlite3

import logging as logger

import helpers

class Context:
    instance = None

    def __init__(self, cfg_file=None):
        L = "__init__"

        self._connection = None

        self.cfg_file = cfg_file or os.path.expanduser("~/.gearshift/gearshift.yaml")
        self.cfg_folder = os.path.abspath(os.path.dirname(self.cfg_file))
        self.cfg = {}

        try:
            with open(self.cfg_file) as fin:
                self.cfg = yaml.safe_load(fin) or self.cfg
        except IOError:
            logger.fatal(f"{L}: {self.cfg_file=} not found")
            sys.exit(1)

        if src_root := self.get("src.root"):
            self.set("src.root", self.resolve_path(src_root))
        else:
            logger.fatal(f"{L}: {self.cfg_file=} has no src.root")
            sys.exit(1)

        if not os.path.isdir(self.src_root_path):
            logger.fatal(f"{L}: {self.cfg_root=} is not a directory")
            sys.exit(1)

        logger.debug(f"{L}: {self.src_root_path=}")
        logger.debug(f"{L}: {self.cfg_file=}")

    @classmethod
    def setup(self, **ad):
        if not Context.instance:
            Context.instance = Context(**ad)

    @property
    def src_root_path(self):
        return self.get("src.root", required=True)
    
    @property
    def db_path(self):
        return self.resolve_path(self.get("src.db", "./gearshift.db"))

    def get(self, keypath:str, default:bool=None, required=False):
        return helpers.get(self.cfg, keypath, default=default, required=required)

    def set(self, keypath:str, value):
        return helpers.set(self.cfg, keypath, value)

    def resolve_path(self, path:str):
        if path.startswith("~"):
            return os.path.normpath(os.path.expanduser(path))
        elif path.startswith("./"):
            return os.path.normpath(os.path.join(self.cfg_folder, path))
        else:
            return path
        
    def cursor(self):
        if not self._connection:
            self._connection = sqlite3.connect(self.db_path)

        cursor = self._connection.cursor()

        return cursor

if __name__ == '__main__':
    context = Context()
    print(context.db)
