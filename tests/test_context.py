import unittest
from unittest.mock import patch

import io
import os
import uuid
import yaml

import gearshift

from ._test_gearshift import (
    TV_IV, TV_PT, key_hash, 
    key_system, key_filename, cfg,
    set_up_key_file, tear_down_key_file,
    encrypted_file_contents,
)

## Run me with:
## python -m unittest tests/*.py

class TestContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_up_key_file()

    @classmethod
    def tearDownClass(cls):
        tear_down_key_file()

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
        self.assertEqual(context.cfg["security"]["key_hash"], key_hash)

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
        self.assertEqual(context.cfg["security"]["key_hash"], key_hash)

    def test_init_with_empty_cfg_file(self):
        cfg_filename = os.path.join(os.path.dirname(__file__), "data", "cfg_file.yaml")

        with io.open(cfg_filename, "w", encoding="utf-8") as fout:
            fout.write("")

        context = gearshift.GearshiftContext(cfg_file=cfg_filename)

        os.remove(cfg_filename)

        self.assertEqual(context.cfg_file, cfg_filename)
        self.assertEqual(context.cfg_folder, os.path.dirname(cfg_filename))
        self.assertEqual(context.cfg, {})

    def test_init_with_no_cfg_file(self):
        cfg_filename = os.path.join(os.path.dirname(__file__), "data", "cfg_file.yaml")

        with self.assertRaises(SystemExit):
            context = gearshift.GearshiftContext(cfg_file=cfg_filename)

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

    def test_aes_encrypt_to_stream(self):
        context = gearshift.GearshiftContext.instance(cfg=cfg)
        encrypted_filename = os.path.join(os.path.dirname(__file__), "data", "encrypted_file.gear")
        with io.open(encrypted_filename, "wb") as fout:
            with patch("base64.urlsafe_b64decode", lambda key: key):
            # base64.urlsafe_b64decode() used by context.server_key()
            # patched because TV_KEY cannot be base64 encoded # see tests/_test_gearshift.py
                with patch("os.urandom", return_value=TV_IV):
                # os.urandom() used by helpers.aes_encrypt()
                # patched because TV_IV is specified # see tests/_test_gearshift.py
                    context.aes_encrypt_to_stream(data=TV_PT, fout=fout) # default key_hash=None

        with io.open(encrypted_filename, "rb") as fin:
            self.assertEqual(fin.read(), encrypted_file_contents)

        os.remove(encrypted_filename)

    def test_aes_decrypt_to_bytes(self):
        context = gearshift.GearshiftContext.instance(cfg=cfg)
        encrypted_filename = os.path.join(os.path.dirname(__file__), "data", "encrypted_file.gear")
        with io.open(encrypted_filename, "wb") as fout:
            fout.write(encrypted_file_contents)

        with io.open(encrypted_filename, "rb") as fin:
            with patch("base64.urlsafe_b64decode", lambda key: key):
            # base64.urlsafe_b64decode() used by context.server_key()
            # patched because TV_KEY cannot be base64 encoded # see tests/_test_gearshift.py
                self.assertEqual(context.aes_decrypt_to_bytes(fin=fin), TV_PT)

        os.remove(encrypted_filename)

if __name__ == '__main__':
    unittest.main()
