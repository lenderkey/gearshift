import base64
import hashlib
import io

import pytest
from cryptography.exceptions import InvalidTag

from gearshift import helpers


def encoded_digest(factory, data):
    return base64.urlsafe_b64encode(factory(data).digest()).decode().rstrip("=")


def test_list_advance_leaves_non_lists_unchanged_and_unwraps_lists():
    assert helpers._list_advance({"key": "value"}, "key", required=False) == {"key": "value"}
    value = [{"key": "value"}]
    assert helpers._list_advance(value, "key", required=False) is value[0]


def test_list_advance_rejects_required_empty_list():
    with pytest.raises(KeyError, match="path"):
        helpers._list_advance([], "path", required=True)


def test_list_advance_treats_optional_empty_list_as_absent():
    assert helpers._list_advance([], "path", required=False) is None


def test_set_creates_and_updates_nested_values():
    data = {}
    assert helpers.set(data, "one.two", 3) is None
    assert data == {"one": {"two": 3}}

    helpers.set(data, "one.two", 4)
    helpers.set(data, "top", True)
    assert data == {"one": {"two": 4}, "top": True}


def test_get_handles_nested_values_defaults_and_required_keys():
    data = {"one": {"two": 2}, "none": None}
    assert helpers.get(data, "one.two") == 2
    assert helpers.get(data, "one.missing", default="fallback") == "fallback"
    assert helpers.get(data, "missing.value", default=7) == 7
    assert helpers.get({"one": []}, "one.two.three", default=9) == 9
    assert helpers.get(None, "key", default=8) == 8

    with pytest.raises(KeyError, match=r"one\.missing"):
        helpers.get(data, "one.missing", required=True)
    with pytest.raises(KeyError, match=r"missing\.value"):
        helpers.get(data, "missing.value", required=True)
    with pytest.raises(AssertionError):
        helpers.get(data, "one.two", required="yes")


def test_get_list_values():
    assert helpers.get({"values": [1, 2]}, "values") == 1
    assert helpers.get({"values": [1, 2]}, "values", first=False) == [1, 2]
    assert helpers.get({"values": []}, "values", default="empty") == "empty"
    with pytest.raises(KeyError, match="values"):
        helpers.get({"values": []}, "values", required=True)


def test_get_advances_through_list_wrapped_mappings():
    assert helpers.get([{"value": 3}], "value") == 3


def test_hash_helpers_are_urlsafe_and_separate_arguments():
    payload = b"a" * 70_000
    assert helpers.sha256_file(io.BytesIO(payload)) == encoded_digest(hashlib.sha256, payload)
    assert helpers.sha256_data("a", b"b") == encoded_digest(hashlib.sha256, b"a@@b")
    assert helpers.md5_data("a", b"b") == encoded_digest(hashlib.md5, b"a@@b")
    assert helpers.sha256_data() == encoded_digest(hashlib.sha256, b"")
    assert helpers.md5_data() == encoded_digest(hashlib.md5, b"")


def test_aes_round_trip_and_authentication():
    key = b"k" * 32
    iv, tag, ciphertext = helpers.aes_encrypt(key, b"secret payload")

    assert len(iv) == 12
    assert helpers.aes_decrypt(key, iv, tag, ciphertext) == b"secret payload"
    with pytest.raises(InvalidTag):
        helpers.aes_decrypt(key, iv, tag, ciphertext + b"corrupt")
