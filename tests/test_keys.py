## Run me with:
## python -m unittest tests/test_keys.py

import unittest
from unittest.mock import patch

import builtins
import os

import gearshift

from ._test_gearshift import (
    TV_KEY, TV_PT, key_hash,
    encrypted_file_contents,
    patched_base64_urlsafe_b64decode,
)

key_system = "fs"
key_filename = os.path.join(os.path.dirname(__file__), "data", "test_keys_key_file.key")
cfg = {
    "security": {
        "key_system": key_system,
        "key_file": key_filename,
        "key_hash": key_hash,
    },
}

# see "SECOND_KEY" and "THIRD_KEY" in tests/data/gcmEncryptExtIV256.rsp
SECOND_KEY = bytes.fromhex("460fc864972261c2560e1eb88761ff1c992b982497bd2ac36c04071cbb8e5d99") # 256 bits
THIRD_KEY = bytes.fromhex("f78a2ba3c5bd164de134a030ca09e99463ea7e967b92c4b0a0870796480297e5") # 256 bits

unencrypted_filename = os.path.join(os.path.dirname(__file__), "data", "test_keys_file")
encrypted_filename = os.path.join(os.path.dirname(__file__), "data", "test_keys_file.gear")

class TestIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = gearshift.GearshiftContext.instance(cfg=cfg)

    def tearDown(self):
        if os.path.exists(key_filename):
            os.remove(key_filename)
        if os.path.exists(unencrypted_filename):
            os.remove(unencrypted_filename)
        if os.path.exists(encrypted_filename):
            os.remove(encrypted_filename)

    def check_read_encrypted_binary_file_success(self):
        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(encrypted_file_contents)

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                self.assertEqual(fin.read(), TV_PT)

    def test_read_encrypted_binary_file_with_two_keys_in_key_file_with_correct_key_first(self):
        with builtins.open(key_filename, "wb") as fout: # keys cannot be base64 encoded
            fout.write(TV_KEY)
            fout.write(b"\n")
            fout.write(SECOND_KEY)

        self.check_read_encrypted_binary_file_success()

    def test_read_encrypted_binary_file_with_two_keys_in_key_file_with_correct_key_last(self):
        with builtins.open(key_filename, "wb") as fout: # keys cannot be base64 encoded
            fout.write(SECOND_KEY)
            fout.write(b"\n")
            fout.write(TV_KEY)

        self.check_read_encrypted_binary_file_success()

    def test_read_encrypted_binary_file_with_three_keys_in_key_file_with_correct_key_first(self):
        with builtins.open(key_filename, "wb") as fout: # keys cannot be base64 encoded
            fout.write(TV_KEY)
            fout.write(b"\n")
            fout.write(SECOND_KEY)
            fout.write(b"\n")
            fout.write(THIRD_KEY)

        self.check_read_encrypted_binary_file_success()

    def test_read_encrypted_binary_file_with_three_keys_in_key_file_with_correct_key_second(self):
        with builtins.open(key_filename, "wb") as fout: # keys cannot be base64 encoded
            fout.write(SECOND_KEY)
            fout.write(b"\n")
            fout.write(TV_KEY)
            fout.write(b"\n")
            fout.write(THIRD_KEY)

        self.check_read_encrypted_binary_file_success()

    def test_read_encrypted_binary_file_with_three_keys_in_key_file_with_correct_key_third(self):
        with builtins.open(key_filename, "wb") as fout: # keys cannot be base64 encoded
            fout.write(SECOND_KEY)
            fout.write(b"\n")
            fout.write(THIRD_KEY)
            fout.write(b"\n")
            fout.write(TV_KEY)

        self.check_read_encrypted_binary_file_success()

if __name__ == '__main__':
    unittest.main()
