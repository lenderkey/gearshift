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
import base64

import logging as logger

import helpers

L = "Context"

class Context:
    instance = None

    def __init__(self, cfg_file=None):
        L = "Context.__init__"

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

        if not os.path.isdir(self.src_root):
            logger.fatal(f"{L}: {self.src_root=} is not a directory")
            sys.exit(1)

        logger.debug(f"{L}: {self.src_root=}")
        logger.debug(f"{L}: {self.cfg_file=}")

    @classmethod
    def setup(self, **ad):
        if not Context.instance:
            Context.instance = Context(**ad)

    @property
    def src_root(self):
        return self.resolve_path(self.get("src.root", required=True))
    
    @property
    def src_host(self):
        return self.get("src.host", required=False)
    
    @property
    def src_url(self):
        return self.get("src.url", required=True)
    
    @property
    def src_user(self):
        return self.get("src.user", required=False)
    
    @property
    def src_pem(self):  
        return self.get("src.pem", required=False)
    
    @property
    def src_token_id(self):  
        return self.get("src.token_id", required=False)
    
    def src_path(self, src_name):
        return os.path.join(self.src_root, src_name)
    
    # @property
    # def dst_root(self):
    #     return self.resolve_path(self.get("dst.root", required=True))
        
    # @property
    # def dst_link_root(self):
    #     links = self.get("dst.links")
    #     if links:
    #         return self.resolve_path(links)
        
    #     return os.path.join(self.dst_root, ".links")
        
    def dst_link_path(self, key_hash:str, data_hash:str) -> str:
       return os.path.join(self.src_root, ".links", key_hash or "plaintext", data_hash[:2], data_hash[2:4], data_hash)

    # def dst_store_path(self, filename) -> str:
    #     assert not os.path.isabs(filename)
    #     return os.path.join(self.dst_root, "store", filename)

    @property
    def db_path(self):
        return self.resolve_path(self.get("src.db", required=True))

    def get(self, keypath:str, default:bool=None, required=False):
        return helpers.get(self.cfg, keypath, default=default, required=required)

    def set(self, keypath:str, value):
        return helpers.set(self.cfg, keypath, value)

    def resolve_path(self, path:str):
        if path is None:
            logger.fatal(f"{L}: {path=} cannot be resolved")
            sys.exit(1)

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
    
    def dst_has_hash(self, data_hash):
        link_filename = self.dst_link_path(data_hash)
        return os.path.exists(link_filename)

    def ingest_link(self, data_hash:str, dst_name:str):
        """
        Will return True if the link exists.
        Consider returning an enumeration.
        """
        L = "Context.ingest_link"

        if os.path.isabs(dst_name):
            raise ValueError(f"{L}: {dst_name=} must be relative")

        link_filename = self.dst_link_path(data_hash)
        link_stbuf = os.stat(link_filename) if os.path.exists(link_filename) else None
        if not link_stbuf:
            logger.debug(f"{L}: {link_filename=} does not exist")
            return False

        dst_filename = self.dst_store_path(dst_name)
        dst_stbuf = os.stat(dst_filename) if os.path.exists(dst_filename) else None

        if dst_stbuf:
            if dst_stbuf.st_ino == link_stbuf.st_ino:
                logger.info(f"{L}: {dst_filename=} already linked to {link_filename=}")
                return True
            
            try:
                os.remove(dst_filename)
                logger.info(f"{L}: removed existing {dst_filename=}")
            except:
                pass

        os.makedirs(os.path.dirname(dst_filename), exist_ok=True)
        os.link(link_filename, dst_filename)

        logger.info(f"{L}: linked {dst_filename=} {link_filename=}")
        return True
    
    def server_key_hash(self) -> str:
        """
        The current key_hash, or None
        """
        return self.get("security.key_hash", required=False) or None
    
    def server_key(self, keyhash:str=None) -> bytes:
        """
        This is the key for encrypting/decrypting files.

        We allow the possibility for multiple keys
        """
        keys_filename = self.get("security.key_file", required=True)
        keys_filename = self.resolve_path(keys_filename)
        keys_hash = keyhash or self.get("security.key_hash", required=True)

        with open(keys_filename, "rb") as fin:
            for key in fin.read().split(b"\n"):
                this_hash = helpers.sha256_data(key)
                if this_hash != keys_hash:
                    continue

                return base64.urlsafe_b64decode(key)
                
        raise ValueError(f"{L}: {keys_filename=} has no key with {keys_hash=}")

if __name__ == '__main__':
    context = Context()
    ## print(context.db)
