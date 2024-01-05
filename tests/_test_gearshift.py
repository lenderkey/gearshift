import io
import os

# GCM test vectors: https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/mac/gcmtestvectors.zip
# see "TEST_VECTOR" in tests/data/gcmEncryptExtIV256.rsp
TV_KEY = bytes.fromhex("31bdadd96698c204aa9ce1448ea94ae1fb4a9a0b3c9d773b51bb1822666b8f22") # 256 bits
TV_IV = bytes.fromhex("0d18e06c7c725ac9e362e1ce") # 96 bits # len(TV_IV) == 12
TV_PT = bytes.fromhex("2db5168e932556f8089a0622981d017d") # 128 bits
TV_CT = bytes.fromhex("fa4362189661d163fcd6a56d8bf0405a") # 128 bits
TV_TAG = bytes.fromhex("d636ac1bbedd5cc3ee727dc2ab4a9489") # 128 bits # len(TV_TAG) == 16

key_hash = "qaj4gLCP7u86X2-PUWIAj45yUWvtCz5vfHPRDoc82Pc" # 256 bits # see generate_tv_key_hash() below
key_hash_bytes = key_hash.encode("ASCII") # len(key_hash_bytes) == 43

key_system = "fs"
key_filename = os.path.join(os.path.dirname(__file__), "data", "key_file.key")
cfg = {
    "security": {
        "key_system": key_system,
        "key_file": key_filename,
        "key_hash": key_hash,
    },
}

def set_up_key_file(): # TV_KEY cannot be base64 encoded
    with io.open(key_filename, "wb") as fout:
        fout.write(TV_KEY)
    # TV_KEY == b'1\xbd\xad\xd9f\x98\xc2\x04\xaa\x9c\xe1D\x8e\xa9J\xe1\xfbJ\x9a\x0b<\x9dw;Q\xbb\x18"fk\x8f"'
    # base64.urlsafe_b64encode(TV_KEY).decode() == 'Mb2t2WaYwgSqnOFEjqlK4ftKmgs8nXc7UbsYImZrjyI='

def tear_down_key_file():
    os.remove(key_filename)

# copied from context.py
BLOCK_KEY_HASH = b"H"
BLOCK_AES_IV = b"I"
BLOCK_AES_TAG = b"T"
BLOCK_END = b"\0"
BLOCK_ZLIB = b"Z" # not allowed (yet)

encrypted_file_header = b"GEAR"
encrypted_file_key_hash_block = BLOCK_KEY_HASH + int(43).to_bytes(1, "big") + key_hash_bytes
encrypted_file_aes_iv_block = BLOCK_AES_IV + int(12).to_bytes(1, "big") + TV_IV
encrypted_file_aes_tag_block = BLOCK_AES_TAG + int(16).to_bytes(1, "big") + TV_TAG
encrypted_file_end_block = BLOCK_END + int(0).to_bytes(1, "big") # int(0).to_bytes(1, "big") == b"\0"

encrypted_file_contents = \
    encrypted_file_header + \
    encrypted_file_key_hash_block + \
    encrypted_file_aes_iv_block + \
    encrypted_file_aes_tag_block + \
    encrypted_file_end_block + \
    TV_CT

def generate_tv_key_hash():
    # used (once) to generate key_hash above
    import base64
    import hashlib
    hasher = hashlib.sha256()
    hasher.update(TV_KEY)
    tv_hash = base64.urlsafe_b64encode(hasher.digest()).decode().rstrip("=")
    print("_test_gearshift.generate_tv_hash:")
    print(f"{tv_hash=}")

# base64.urlsafe_b64decode() used by context.server_key()
# patched because TV_KEY cannot be base64 encoded
def patched_base64_urlsafe_b64decode(s):
    return s

# os.urandom() used by helpers.aes_encrypt()
# patched because TV_IV is specified
def patched_os_urandom(size):
    return TV_IV

TEXT_PT = "Hello, world!"
encrypted_text_pt_filename = os.path.join(os.path.dirname(__file__), "data", "text_pt.gear")

def generate_encrypted_text_file():
    # used (once) to generate tests/data/text_pt.gear
    from unittest.mock import patch
    import gearshift
    
    set_up_key_file()
    context = gearshift.GearshiftContext.instance(cfg=cfg)

    with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
        with patch("os.urandom", patched_os_urandom):
            with gearshift.io.open(encrypted_text_pt_filename, mode="w", context=context) as fout:
                fout.write(TEXT_PT)
    
    tear_down_key_file()

EMPTY_PT = b""
encrypted_empty_pt_filename = os.path.join(os.path.dirname(__file__), "data", "empty_pt.gear")

def generate_encrypted_binary_file_with_empty_plaintext():
    # used (once) to generate tests/data/empty_pt.gear
    from unittest.mock import patch
    import gearshift
    
    set_up_key_file()
    context = gearshift.GearshiftContext.instance(cfg=cfg)

    with patch("base64.urlsafe_b64decode", patched_base64_urlsafe_b64decode):
        with patch("os.urandom", patched_os_urandom):
            with gearshift.io.open(encrypted_empty_pt_filename, mode="wb", context=context) as fout:
                fout.write(EMPTY_PT)
    
    tear_down_key_file()
