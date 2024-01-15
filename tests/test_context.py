## Run me with:
## python -m unittest tests/test_context.py

import unittest
from unittest.mock import patch, MagicMock

import base64
import io
import os
import uuid
import yaml

import gearshift

from ._test_gearshift import (
    TV_KEY, TV_PT, tv_key_hash, 
    encrypted_file_contents,
    generate_key_hash,
    patched_base64_urlsafe_b64decode, patched_os_urandom,
)

key_system = "fs"
key_filename = os.path.join(os.path.dirname(__file__), "data", "test_context_key_file.key")
cfg = {
    "security": {
        "key_system": key_system,
        "key_file": key_filename,
        "key_hash": tv_key_hash,
    },
}

class TestContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with io.open(key_filename, "wb") as fout:
            fout.write(TV_KEY) # TV_KEY cannot be base64 encoded for encryption/decryption

    @classmethod
    def tearDownClass(cls):
        os.remove(key_filename)

    def test_init_with_default_cfg_file(self):
        default_cfg_filename = "~/.gearshift/gearshift.yaml"

        renamed_existing_cfg_filename = None
        if os.path.exists(os.path.expanduser(default_cfg_filename)):
            renamed_existing_cfg_filename = f"{os.path.expanduser(default_cfg_filename)}.{str(uuid.uuid4())}"
            os.rename(os.path.expanduser(default_cfg_filename), renamed_existing_cfg_filename)

        with io.open(os.path.expanduser(default_cfg_filename), "w", encoding="utf-8") as fout:
            yaml.dump(cfg, fout)        

        context = gearshift.GearshiftContext()

        os.remove(os.path.expanduser(default_cfg_filename))

        if renamed_existing_cfg_filename:
            os.rename(renamed_existing_cfg_filename, os.path.expanduser(default_cfg_filename))

        self.assertEqual(context.cfg_file, os.path.expanduser(default_cfg_filename))
        self.assertEqual(context.cfg_folder, os.path.dirname(os.path.expanduser(default_cfg_filename)))
        self.assertEqual(context.cfg["security"]["key_system"], key_system)
        self.assertEqual(context.cfg["security"]["key_file"], key_filename)
        self.assertEqual(context.cfg["security"]["key_hash"], tv_key_hash)

    def test_init_with_specified_cfg_file(self):
        cfg_filename = os.path.join(os.path.dirname(__file__), "data", "cfg_file.yaml")

        with io.open(cfg_filename, "w", encoding="utf-8") as fout:
            yaml.dump(cfg, fout)

        context = gearshift.GearshiftContext(cfg_file=cfg_filename)

        os.remove(cfg_filename)

        self.assertEqual(context.cfg_file, cfg_filename)
        self.assertEqual(context.cfg_folder, os.path.dirname(cfg_filename))
        self.assertEqual(context.cfg["security"]["key_system"], key_system)
        self.assertEqual(context.cfg["security"]["key_file"], key_filename)
        self.assertEqual(context.cfg["security"]["key_hash"], tv_key_hash)

    def test_init_with_empty_cfg_file(self):
        cfg_filename = os.path.join(os.path.dirname(__file__), "data", "cfg_file.yaml")

        with io.open(cfg_filename, "w", encoding="utf-8") as fout:
            fout.write("")

        context = gearshift.GearshiftContext(cfg_file=cfg_filename)

        os.remove(cfg_filename)

        self.assertEqual(context.cfg_file, cfg_filename)
        self.assertEqual(context.cfg_folder, os.path.dirname(cfg_filename))
        self.assertEqual(context.cfg, {})

    def test_init_with_no_cfg_file_and_not_cfg_optional(self):
        cfg_filename = os.path.join(os.path.dirname(__file__), "data", "cfg_file.yaml")

        with self.assertRaises(ValueError): # GearshiftNoContextError(ValueError)
            context = gearshift.GearshiftContext(cfg_file=cfg_filename) # default cfg_optional=False

    @unittest.skip
    def test_init_with_no_cfg_file_and_cfg_optional(self):
        # TODO
        pass

    def test_instance(self):
        context = gearshift.GearshiftContext.instance(cfg=cfg)
        second_cfg = {
            "security": {
                "key_system": "foo",
                "key_file": "bar",
                "key_hash": "baz",
            },
        }
        second_context = gearshift.GearshiftContext.instance(cfg=second_cfg)

        self.assertIs(second_context, context)

    def test_server_key_fs(self):
        # okay to base64 encode TV_KEY here
        # because not doing any encryption/decryption
        fs_key = base64.urlsafe_b64encode(TV_KEY)
        fs_key_hash = generate_key_hash(fs_key)
        fs_key_filename = os.path.join(os.path.dirname(__file__), "data", "test_server_key_file.key")
        fs_cfg = {
            "security": {
                "key_system": "fs",
                "key_file": fs_key_filename,
                "key_hash": fs_key_hash,
            },
        }
        with io.open(fs_key_filename, "wb") as fout:
            fout.write(fs_key)

        context = gearshift.GearshiftContext(cfg=fs_cfg)
        key, key_hash = context.server_key() # default key_hash=None

        self.assertEqual(key, TV_KEY)
        self.assertEqual(key_hash, fs_key_hash)

        os.remove(fs_key_filename)

    @patch("boto3.session.Session", autospec=True)
    def test_server_key_aws(self, mock_session:MagicMock):
        import json

        # okay to base64 encode TV_KEY here
        # because not doing any encryption/decryption
        aws_key = base64.urlsafe_b64encode(TV_KEY)
        aws_key_hash = generate_key_hash(aws_key)
        aws_cfg = {
            "security": {
                "key_system": "aws",
                "secret_name": "foo",
                "key_hash": aws_key_hash,
                # "aws_access_key_id": _, 
                # "aws_secret_access_key": _,
                # "region_name": _, 
                # "profile_name": _,
            },
        }
        secret = {
            aws_key_hash: aws_key.decode()
        }
        mock_session.return_value.client.return_value.get_secret_value.return_value = {
            "SecretString": json.dumps(secret),
        }

        context = gearshift.GearshiftContext(cfg=aws_cfg)
        key, key_hash = context.server_key() # default key_hash=None

        self.assertEqual(key, TV_KEY)
        self.assertEqual(key_hash, aws_key_hash)

        mock_session.assert_called_once_with()
        clientd = {
            "service_name": "secretsmanager",
            "region_name": "ca-central-1",
        }
        mock_session.return_value.client.assert_called_once_with(**clientd)
        mock_client = mock_session.return_value.client.return_value
        mock_client.get_secret_value.assert_called_once_with(
            SecretId=aws_cfg["security"]["secret_name"]
        )

    def test_aes_encrypt_to_stream(self):
        context = gearshift.GearshiftContext(cfg=cfg)
        encrypted_filename = os.path.join(os.path.dirname(__file__), "data", "encrypted_file.gear")
        with io.open(encrypted_filename, "wb") as fout:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                with patch("os.urandom", patched_os_urandom):
                    context.aes_encrypt_to_stream(data=TV_PT, fout=fout) # default key_hash=None

        with io.open(encrypted_filename, "rb") as fin:
            self.assertEqual(fin.read(), encrypted_file_contents)

        os.remove(encrypted_filename)

    def test_aes_decrypt_to_bytes(self):
        context = gearshift.GearshiftContext(cfg=cfg)
        encrypted_filename = os.path.join(os.path.dirname(__file__), "data", "encrypted_file.gear")
        with io.open(encrypted_filename, "wb") as fout:
            fout.write(encrypted_file_contents)

        with io.open(encrypted_filename, "rb") as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                self.assertEqual(context.aes_decrypt_to_bytes(fin=fin), TV_PT)

        os.remove(encrypted_filename)

if __name__ == '__main__':
    unittest.main()
