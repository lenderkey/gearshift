#
#   Gearshift.py
#
#   David Janes
#   Gearshift
#   2023-03-23
#

from typing import Tuple, Union, ForwardRef

import yaml
import os
import sys
import sqlite3
import base64
import io

import logging as logger

hvac = ForwardRef("hvac")

L = "GearshiftContext"

class GearshiftNoContextError(ValueError):
    pass

class GearshiftContext:
    _instance = None

    BLOCK_AES_IV = b"I"
    BLOCK_AES_TAG = b"T"
    BLOCK_KEY_HASH = b"H"
    BLOCK_ZLIB = b"Z"
    BLOCK_END = b"\0"

    def __init__(self, cfg_file:str=None, cfg:dict=None, cfg_optional:bool=False):
        L = "Gearshift.__init__"

        self._connection = None

        self.cfg_file = cfg_file or os.path.expanduser("~/.gearshift/gearshift.yaml")
        self.cfg_folder = os.path.abspath(os.path.dirname(self.cfg_file))
        self.cfg = {}

        if cfg is not None:
            self.cfg = cfg
        else:
            try:
                with open(self.cfg_file) as fin:
                    self.cfg = yaml.safe_load(fin) or self.cfg
            except IOError:
                if cfg_optional:
                    self.cfg = {}
                else:
                    logger.fatal(f"{L}: {self.cfg_file=} not found")
                    raise GearshiftNoContextError(f"{L}: {self.cfg_file=} not found")

    @classmethod
    def instance(self, **ad) -> "GearshiftContext":
        if not GearshiftContext._instance:
            GearshiftContext._instance = GearshiftContext(**ad)

        return GearshiftContext._instance
    
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
    def src_folder(self):
        """
        This lets you sync a subfolder of the source only
        """
        return self.get("src.folder", required=False) or "/"
    
    @property
    def src_pem(self):  
        return self.get("src.pem", required=False)
    
    @property
    def src_token_id(self):  
        return self.get("src.token_id", required=False)
    
    def src_path(self, src_name):
        return os.path.join(self.src_root, src_name)
    
    def dst_link_path(self, key_hash:str, data_hash:str) -> str:
       return os.path.join(self.src_root, ".links", key_hash or "plaintext", data_hash[:2], data_hash[2:4], data_hash)

    def get(self, keypath:str, default:bool=None, required=False):
        from .helpers import get
        return get(self.cfg, keypath, default=default, required=required)

    def set(self, keypath:str, value):
        from .helpers import set
        return set(self.cfg, keypath, value)

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
        
    def dst_has_hash(self, data_hash):
        link_filename = self.dst_link_path(data_hash)
        return os.path.exists(link_filename)

    def ingest_link(self, data_hash:str, dst_name:str):
        """
        Will return True if the link exists.
        Consider returning an enumeration.
        """
        L = "Gearshift.ingest_link"

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
    
    def server_key(self, key_hash:str=None) -> Tuple[bytes, str]:
        """
        This is the key for encrypting/decrypting files.

        We allow the possibility for multiple keys
        """
        from .helpers import sha256_data

        match self.get("security.key_system") or "fs":
            case "vault":
                key_hash = key_hash or "current" 
                key_root = self.get_vault_key_root()
                key_group = self.get_vault_key_group()
                vault_client = self.get_vault_client()
                key_path = f"{key_root}/{key_group}/{key_hash}"
                try:
                    read_response = vault_client.secrets.kv.v2.read_secret(
                        path=key_path,
                    )
                except hvac.exceptions.InvalidPath:
                    raise KeyError(f"{L}: key not found: {key_path}")

                data = read_response.get('data', {})
                data = data.get('data', {})
                key_encoded = data.get('key')
                key = base64.urlsafe_b64decode(key_encoded)
                key_hash = data.get('key_hash')
                if not key or not key_hash:
                    raise KeyError(f"{L}: key not found: {key_path} [2]")

                return key, key_hash

            case "fs":
                if not key_hash:
                    key_hash = self.server_key_hash()

                keys_filename = self.get("security.key_file", required=True)
                keys_filename = self.resolve_path(keys_filename)
                keys_hash = key_hash or self.get("security.key_hash", required=True)

                with open(keys_filename, "rb") as fin:
                    for key in fin.read().split(b"\n"):
                        this_hash = sha256_data(key)
                        if this_hash != keys_hash:
                            continue

                        return base64.urlsafe_b64decode(key), key_hash
                        
                raise ValueError(f"{L}: {keys_filename=} has no key with {keys_hash=}")
            
            case "aws":
                ## note you have to do `pip install boto3`
                import json
                import boto3
                from botocore.exceptions import ClientError

                secret_name = self.get("security.secret_name", required=True)
                region_name = self.get("security.region_name", required=False, default="ca-central-1")

                # Create a Secrets Manager client
                session = boto3.session.Session()
                client = session.client(
                    service_name='secretsmanager',
                    region_name=region_name
                )

                try:
                    get_secret_value_response = client.get_secret_value(
                        SecretId=secret_name
                    )
                except ClientError as x:
                    logger.error(f"{L}: {x=}")
                    raise

                secrets = get_secret_value_response['SecretString']
                secretd = json.loads(secrets)

                if key_hash not in secretd:
                    raise KeyError(f"{L}: key not found: {key_hash}")
                
                key = base64.urlsafe_b64decode(secretd[key_hash])
                return key, key_hash
            
            case _:
                raise ValueError(f"{L}: unknown key_system: {self.get('security.key_system')}")


    def aes_encrypt_to_stream(self, data:bytes, fout:io.BytesIO, key_hash:str=None) -> None:
        from .helpers import aes_encrypt

        key, key_hash = self.server_key(key_hash)

        key_hash_bytes = key_hash.encode("ASCII")
        aes_iv, aes_tag, aes_ciphertext = aes_encrypt(key, data)

        fout.write(b"GEAR")

        fout.write(GearshiftContext.BLOCK_KEY_HASH)
        fout.write(len(key_hash_bytes).to_bytes(1, "big"))
        fout.write(key_hash_bytes)

        fout.write(GearshiftContext.BLOCK_AES_IV)
        fout.write(len(aes_iv).to_bytes(1, "big"))
        fout.write(aes_iv)

        fout.write(GearshiftContext.BLOCK_AES_TAG)
        fout.write(len(aes_tag).to_bytes(1, "big"))
        fout.write(aes_tag)

        fout.write(GearshiftContext.BLOCK_END)
        fout.write(b"\0")

        fout.write(aes_ciphertext)

    def aes_decrypt_to_bytes(self, fin:io.BytesIO) -> bytes:
        from .helpers import aes_decrypt
        import string

        header = fin.read(4)
        assert header == b"GEAR"

        key_hash = None
        aes_iv = None
        aes_tag = None

        stop = False
        while not stop:
            block_tag = fin.read(1)
            if block_tag is None:
                break

            block_length = fin.read(1) or 0

            match block_tag:
                case GearshiftContext.BLOCK_END:
                    stop = True
                case GearshiftContext.BLOCK_AES_IV:
                    aes_iv = fin.read(int.from_bytes(block_length, "big"))
                case GearshiftContext.BLOCK_AES_TAG:
                    aes_tag = fin.read(int.from_bytes(block_length, "big"))
                case GearshiftContext.BLOCK_KEY_HASH:
                    key_hash = fin.read(int.from_bytes(block_length, "big"))
                    key_hash = key_hash.decode("ASCII")
                case otherwise:
                    if block_tag in string.ascii_uppercase.encode("ASCII"):
                        raise ValueError(f"{L}: unknown (required) block tag: {block_tag}")
                    
                    logger.info(f"{L}: unknown (optional) block tag: {block_tag}")

        assert aes_iv
        assert aes_tag
        assert key_hash

        # key_hash_len = int(fin.read(1)[0])
        # key_hash = fin.read(key_hash_len).decode("ASCII")
        # aes_iv_len = int(fin.read(1)[0])
        # aes_iv = fin.read(aes_iv_len)
        # aes_tag_len = int(fin.read(1)[0])
        # aes_tag = fin.read(aes_tag_len)

        data = fin.read()
        key, _ = self.server_key(key_hash)     
        
        return aes_decrypt(key, iv=aes_iv, tag=aes_tag, ciphertext=data)
    
    def get_vault_key_root(self) -> str:
        return "gearshift-keys"
    
    def get_vault_key_group(self) -> str:
        """
        """
        return self.get("vault.key_group", required=False) or "default"
    
    def get_vault_client(self) -> "hvac.Client":
        import hvac

        L = "Gearshift.get_vault_client"

        vault_client = hvac.Client(
            url='http://127.0.0.1:8200',  # Replace with your Vault address
            ## token='s.xxxxxxx'  # Replace with your Vault token
        )

        # Check if the client is authenticated
        if not vault_client.is_authenticated():
            raise PermissionError("Authentication failed")
        
        logger.debug(f"{L}: {vault_client=}")
        return vault_client

if __name__ == '__main__':
    context = GearshiftContext()
    ## print(context.db)
