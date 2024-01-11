## Run me with:
## python -m unittest tests/test_io.py

import unittest
from unittest.mock import patch

import builtins
import os
import string

import gearshift

from ._test_gearshift import (
    TV_KEY, TV_PT, TV_CT, tv_key_hash,
    BLOCK_KEY_HASH, BLOCK_AES_IV, BLOCK_AES_TAG, BLOCK_END,
    encrypted_file_header,
    encrypted_file_key_hash_block,
    encrypted_file_aes_iv_block,
    encrypted_file_aes_tag_block,
    encrypted_file_end_block,
    encrypted_file_contents,
    patched_base64_urlsafe_b64decode, patched_os_urandom,
    TEXT_PT, encrypted_text_pt_filename,
    EMPTY_PT, encrypted_empty_pt_filename,
)

key_system = "fs"
key_filename = os.path.join(os.path.dirname(__file__), "data", "test_io_key_file.key")
cfg = {
    "security": {
        "key_system": key_system,
        "key_file": key_filename,
        "key_hash": tv_key_hash,
    },
}

unencrypted_filename = os.path.join(os.path.dirname(__file__), "data", "test_io_file")
encrypted_filename = os.path.join(os.path.dirname(__file__), "data", "test_io_file.gear")

class TestIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with builtins.open(key_filename, "wb") as fout:
            fout.write(TV_KEY) # TV_KEY cannot be base64 encoded
        cls.context = gearshift.GearshiftContext.instance(cfg=cfg)

    @classmethod
    def tearDownClass(cls):
        os.remove(key_filename)

    def tearDown(self):
        if os.path.exists(unencrypted_filename):
            os.remove(unencrypted_filename)
        if os.path.exists(encrypted_filename):
            os.remove(encrypted_filename)

    def test_read_unencrypted_text_file(self):
        with builtins.open(unencrypted_filename, "w", encoding="utf-8") as fout:
            fout.write(TEXT_PT)

        with gearshift.io.open(unencrypted_filename, mode="r", context=self.context) as fin: # default encoding="utf-8"
            self.assertEqual(fin.read(), TEXT_PT)

    def test_read_unencrypted_binary_file(self):
        with builtins.open(unencrypted_filename, "wb") as fout:
            fout.write(TV_PT)

        with gearshift.io.open(unencrypted_filename, mode="rb", context=self.context) as fin:
            self.assertEqual(fin.read(), TV_PT)

    def test_read_encrypted_text_file(self):
        # see generate_encrypted_text_file() in tests/_test_gearshift.py
        with gearshift.io.open(encrypted_text_pt_filename, mode="r", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                self.assertEqual(fin.read(), TEXT_PT)

    @unittest.skip
    def test_read_encrypted_text_file_with_encoding(self):
        # TODO
        pass

    def test_read_encrypted_binary_file(self):
        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(encrypted_file_contents)

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                self.assertEqual(fin.read(), TV_PT)

    def test_read_encrypted_binary_file_with_empty_plaintext(self):
        # see generate_encrypted_binary_file_with_empty_plaintext() in tests/_test_gearshift.py
        with gearshift.io.open(encrypted_empty_pt_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                self.assertEqual(fin.read(), EMPTY_PT)

    def test_read_encrypted_binary_file_with_blocks_out_of_order(self):
        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(
                encrypted_file_header +
                encrypted_file_aes_tag_block +
                encrypted_file_aes_iv_block +
                encrypted_file_key_hash_block +
                encrypted_file_end_block +
                TV_CT
            )

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                self.assertEqual(fin.read(), TV_PT)

    def test_read_encrypted_binary_file_with_optional_letter_block_type(self):
        for block_type in [letter.encode("ASCII") for letter in string.ascii_lowercase]:
            with builtins.open(encrypted_filename, "wb") as fout:
                fout.write(
                    encrypted_file_header +
                    encrypted_file_key_hash_block +
                    encrypted_file_aes_iv_block +
                    encrypted_file_aes_tag_block +
                    block_type + int(0).to_bytes(1, "big") +
                    encrypted_file_end_block +
                    TV_CT
                )

            with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
                with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                    self.assertEqual(fin.read(), TV_PT)

    def test_read_encrypted_binary_file_with_valid_duplicate_block_after_invalid_block(self):
        for block_type in [BLOCK_KEY_HASH, BLOCK_AES_IV, BLOCK_AES_TAG]:
            with builtins.open(encrypted_filename, "wb") as fout:
                fout.write(
                    encrypted_file_header +
                    block_type + int(0).to_bytes(1, "big") +
                    encrypted_file_key_hash_block +
                    encrypted_file_aes_iv_block +
                    encrypted_file_aes_tag_block +
                    encrypted_file_end_block +
                    TV_CT
                )

            with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
                with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                    self.assertEqual(fin.read(), TV_PT)

    def test_read_encrypted_binary_file_with_invalid_duplicate_block_after_valid_block(self):
        for block_type in [BLOCK_KEY_HASH, BLOCK_AES_IV, BLOCK_AES_TAG]:
            with builtins.open(encrypted_filename, "wb") as fout:
                fout.write(
                    encrypted_file_header +
                    encrypted_file_key_hash_block +
                    encrypted_file_aes_iv_block +
                    encrypted_file_aes_tag_block +
                    block_type + int(0).to_bytes(1, "big") +
                    encrypted_file_end_block +
                    TV_CT
                )

            with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
                with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                    with self.assertRaises(AssertionError):
                        fin.read()

    def test_read_encrypted_binary_file_with_header_missing(self):
        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(
                encrypted_file_key_hash_block +
                encrypted_file_aes_iv_block +
                encrypted_file_aes_tag_block +
                encrypted_file_end_block +
                TV_CT
            )

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                with self.assertRaises(AssertionError):
                    fin.read()

    def test_read_encrypted_binary_file_with_block_missing(self):
        blocks = [
            encrypted_file_key_hash_block,
            encrypted_file_aes_iv_block,
            encrypted_file_aes_tag_block,
        ]
        for missing_block in blocks:
            with builtins.open(encrypted_filename, "wb") as fout:
                fout.write(encrypted_file_header)
                for block in blocks:
                    if block == missing_block:
                        continue
                    fout.write(block)
                fout.write(encrypted_file_end_block)
                fout.write(TV_CT)

            with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
                with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                    with self.assertRaises(AssertionError):
                        fin.read()

    def test_read_encrypted_binary_file_with_end_block_missing(self):
        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(
                encrypted_file_header +
                encrypted_file_key_hash_block +
                encrypted_file_aes_iv_block +
                encrypted_file_aes_tag_block +
                TV_CT
            )

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                with self.assertRaises(ValueError):
                # interprets first byte of TV_CT as block type
                    fin.read()

    def test_read_encrypted_binary_file_with_empty_plaintext_with_end_block_missing(self):
        # see generate_encrypted_binary_file_with_empty_plaintext() in tests/_test_gearshift.py
        with builtins.open(encrypted_empty_pt_filename, "rb") as fin:
            encrypted_empty_pt_file_contents = fin.read()

        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(encrypted_empty_pt_file_contents[:-2])

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                with self.assertRaises(ValueError):
                    fin.read()

    def test_read_encrypted_binary_file_with_empty_plaintext_with_end_block_length_missing(self):
        # see generate_encrypted_binary_file_with_empty_plaintext() in tests/_test_gearshift.py
        with builtins.open(encrypted_empty_pt_filename, "rb") as fin:
            encrypted_empty_pt_file_contents = fin.read()

        with builtins.open(encrypted_filename, "wb") as fout:
            fout.write(encrypted_empty_pt_file_contents[:-1])

        with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
            with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                with self.assertRaises(ValueError):
                    fin.read()

    def test_read_encrypted_binary_file_with_invalid_letter_block_type(self):
        valid_uppercase_letter_block_types = [BLOCK_KEY_HASH, BLOCK_AES_IV, BLOCK_AES_TAG] # BLOCK_ZLIB not allowed (yet)
        for block_type in [letter.encode("ASCII") for letter in string.ascii_uppercase]:
            if block_type in valid_uppercase_letter_block_types:
                continue
            with builtins.open(encrypted_filename, "wb") as fout:
                fout.write(
                    encrypted_file_header +
                    encrypted_file_key_hash_block +
                    encrypted_file_aes_iv_block +
                    encrypted_file_aes_tag_block +
                    block_type + int(0).to_bytes(1, "big") +
                    encrypted_file_end_block +
                    TV_CT
                )

            with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
                with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                    with self.assertRaises(ValueError):
                        fin.read()
            
    def test_read_encrypted_binary_file_with_non_letter_block_type(self):
        for block_type in [bytes([code]) for code in range(256) if code not in string.ascii_letters.encode("ASCII")]:
            if block_type == BLOCK_END:
                continue
            with builtins.open(encrypted_filename, "wb") as fout:
                fout.write(
                    encrypted_file_header +
                    encrypted_file_key_hash_block +
                    encrypted_file_aes_iv_block +
                    encrypted_file_aes_tag_block +
                    block_type + int(0).to_bytes(1, "big") +
                    encrypted_file_end_block +
                    TV_CT
                )

            with gearshift.io.open(encrypted_filename, mode="rb", context=self.context) as fin:
                with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
                    with self.assertRaises(ValueError):
                        fin.read()
            
    def test_write_encrypted_text_file(self):
        # see generate_encrypted_text_file() in tests/_test_gearshift.py
        with builtins.open(encrypted_text_pt_filename, "rb") as fin:
            encrypted_text_pt_file_contents = fin.read()

        with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
            with patch("os.urandom", patched_os_urandom):
                with gearshift.io.open(encrypted_filename, mode="w", context=self.context) as fout:
                    fout.write(TEXT_PT)

        with builtins.open(encrypted_filename, "rb") as fin:
            self.assertEqual(fin.read(), encrypted_text_pt_file_contents)

    @unittest.skip
    def test_write_encrypted_text_file_with_encoding(self):
        # TODO
        pass

    def test_write_encrypted_binary_file(self):
        with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
            with patch("os.urandom", patched_os_urandom):
                with gearshift.io.open(encrypted_filename, mode="wb", context=self.context) as fout:
                    fout.write(TV_PT)

        with builtins.open(encrypted_filename, "rb") as fin:
            self.assertEqual(fin.read(), encrypted_file_contents)

    def test_write_encrypted_binary_file_with_empty_plaintext(self):
        # see generate_encrypted_binary_file_with_empty_plaintext() in tests/_test_gearshift.py
        with builtins.open(encrypted_empty_pt_filename, "rb") as fin:
            encrypted_empty_pt_file_contents = fin.read()

        with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
            with patch("os.urandom", patched_os_urandom):
                with gearshift.io.open(encrypted_filename, mode="wb", context=self.context) as fout:
                    fout.write(EMPTY_PT)

        with builtins.open(encrypted_filename, "rb") as fin:
            self.assertEqual(fin.read(), encrypted_empty_pt_file_contents)

    def test_invalid_modes(self):
        valid_filename = os.path.join(os.path.dirname(__file__), "data", "valid_file")
        invalid_modes = [
            "rt", "r+", "r+t", "r+b", # note "r" (valid) == "rt" (invalid)
            "wt", "w+", "w+t", "w+b", # note "w" (valid) == "wt" (invalid)
            "x", "xt", "x+", "x+t", "xb", "x+b",
            "a", "at", "a+", "a+t", "ab", "a+b", "foo"]
        
        for invalid_mode in invalid_modes:
            with self.assertRaises(ValueError):
                with gearshift.io.open(valid_filename, mode=invalid_mode, context=self.context) as fio: # default encoding="utf-8"
                    pass

    @unittest.expectedFailure
    def test_invalid_modes_without_context_manager(self):
        valid_filename = os.path.join(os.path.dirname(__file__), "data", "valid_file")
        invalid_modes = [
            "rt", "r+", "r+t", "r+b", # note "r" (valid) == "rt" (invalid)
            "wt", "w+", "w+t", "w+b", # note "w" (valid) == "wt" (invalid)
            "x", "xt", "x+", "x+t", "xb", "x+b",
            "a", "at", "a+", "a+t", "ab", "a+b", "foo"]
        
        for invalid_mode in invalid_modes:
            with self.assertRaises(ValueError):
                fio = gearshift.io.open(valid_filename, mode=invalid_mode, context=self.context) # default encoding="utf-8"

if __name__ == '__main__':
    unittest.main()
