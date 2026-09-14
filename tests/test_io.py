import io
import os
from dataclasses import is_dataclass
from unittest.mock import Mock

import pytest

import gearshift
import gearshift.io as gearshift_io


def test_text_and_binary_encrypted_round_trip(tmp_path, test_context):
    text_file = tmp_path / "hello.txt"
    text_file.write_text("old plaintext", encoding="utf-8")
    with gearshift.open(text_file.as_posix(), "w", encoding="utf-16", context=test_context) as output:
        assert output.write("Hello, world!") is None
        assert output.flush() is None

    assert not text_file.exists()
    assert (tmp_path / "hello.txt.gear").exists()
    with gearshift.open(text_file.as_posix() + ".gear", "r", encoding="utf-16", context=test_context) as source:
        assert source.read(5) == "Hello"
        assert source.read(100) == ", world!"
        assert source.read(1) == ""

    binary_file = tmp_path / "binary"
    with gearshift.open(binary_file.as_posix(), "wb", context=test_context, remove_on_write=False) as output:
        output.write(b"\x00\x01data")
    with gearshift.open(binary_file.as_posix(), "rb", context=test_context) as source:
        assert source.read() == b"\x00\x01data"


def test_plaintext_fallback_for_text_and_binary(tmp_path, test_context):
    text_file = tmp_path / "plain.txt"
    text_file.write_text("plain text", encoding="utf-8")
    with gearshift.open(text_file.as_posix(), "r", context=test_context) as source:
        assert source.read(5) == "plain"
        assert source.read() == " text"

    binary_file = tmp_path / "plain.bin"
    binary_file.write_bytes(b"binary")
    with gearshift.open(binary_file.as_posix(), "rb", context=test_context) as source:
        assert source.read() == b"binary"


def test_constructor_uses_default_context_and_strips_suffix(monkeypatch, test_context):
    instance = Mock(return_value=test_context)
    monkeypatch.setattr("gearshift.context.GearshiftContext.instance", instance)
    stream = gearshift.Gearshift("file.gear", unused=True)
    assert stream.filename == "file"
    assert stream.filename_gear == "file.gear"
    assert stream.context is test_context
    instance.assert_called_once_with()


def test_unsupported_mode_and_operations(tmp_path, test_context):
    stream = gearshift.Gearshift((tmp_path / "file").as_posix(), "a", context=test_context)
    with pytest.raises(ValueError, match="Unsupported mode"):
        stream.__enter__()

    stream = gearshift.Gearshift((tmp_path / "file").as_posix(), "r", context=test_context)
    with pytest.raises(io.UnsupportedOperation, match="not writable"):
        stream.write("data")
    assert stream.__exit__(None, None, None) is None

    stream = gearshift.Gearshift((tmp_path / "file").as_posix(), "w", context=test_context)
    with pytest.raises(io.UnsupportedOperation, match="not readable"):
        stream.read()


def test_write_exception_removes_temporary_file(tmp_path, test_context):
    stream = gearshift.Gearshift((tmp_path / "file").as_posix(), "w", context=test_context)
    message = "stop"
    with pytest.raises(RuntimeError, match="stop"):
        with stream:
            temporary = stream.filename_tmp
            assert os.path.exists(temporary)
            raise RuntimeError(message)
    assert stream.filename_tmp is None
    assert not os.path.exists(temporary)
    assert not (tmp_path / "file.gear").exists()


def test_write_preserves_plaintext_when_requested(tmp_path, test_context):
    plaintext = tmp_path / "file"
    plaintext.write_bytes(b"original")
    with gearshift.Gearshift(plaintext.as_posix(), "wb", context=test_context, remove_on_write=False) as output:
        output.write(b"encrypted")
    assert plaintext.read_bytes() == b"original"


def test_multiple_writes_form_one_readable_file(tmp_path, test_context):
    filename = tmp_path / "file"
    with gearshift.open(filename.as_posix(), "w", context=test_context) as output:
        output.write("first")
        output.write(" second")
    with gearshift.open(filename.as_posix(), "r", context=test_context) as source:
        assert source.read() == "first second"


def test_unbounded_read_returns_only_remaining_data(tmp_path, test_context):
    filename = tmp_path / "file"
    with gearshift.open(filename.as_posix(), "w", context=test_context) as output:
        output.write("payload")
    with gearshift.open(filename.as_posix(), "r", context=test_context) as source:
        assert source.read(3) == "pay"
        assert source.read() == "load"


def test_strip_and_exists_cover_plain_and_encrypted_names(tmp_path):
    plain = tmp_path / "file"
    encrypted = tmp_path / "file.gear"
    assert gearshift.strip(encrypted.as_posix()) == plain.as_posix()
    assert gearshift.strip(plain.as_posix()) == plain.as_posix()
    assert not gearshift.exists(plain.as_posix())

    encrypted.write_bytes(b"encrypted")
    assert gearshift.exists(encrypted.as_posix())
    assert gearshift.exists(plain.as_posix())
    encrypted.unlink()
    plain.write_bytes(b"plain")
    assert gearshift.exists(plain.as_posix())


def test_is_encrypted_and_is_unencrypted(tmp_path):
    plain = tmp_path / "file"
    encrypted = tmp_path / "file.gear"

    assert not gearshift.is_encrypted(plain.as_posix())
    assert not gearshift.is_encrypted(encrypted.as_posix())
    assert not gearshift.is_unencrypted(plain.as_posix())
    assert not gearshift.is_unencrypted(encrypted.as_posix())

    plain.write_bytes(b"plain")
    assert not gearshift.is_encrypted(plain.as_posix())
    assert not gearshift.is_encrypted(encrypted.as_posix())
    assert gearshift.is_unencrypted(plain.as_posix())
    assert gearshift.is_unencrypted(encrypted.as_posix())

    encrypted.write_bytes(b"encrypted")
    assert gearshift.is_encrypted(plain.as_posix())
    assert gearshift.is_encrypted(encrypted.as_posix())
    assert not gearshift.is_unencrypted(plain.as_posix())
    assert not gearshift.is_unencrypted(encrypted.as_posix())

    plain.unlink()
    assert gearshift.is_encrypted(plain.as_posix())
    assert gearshift.is_encrypted(encrypted.as_posix())
    assert not gearshift.is_unencrypted(plain.as_posix())
    assert not gearshift.is_unencrypted(encrypted.as_posix())


def test_remove_deletes_both_forms_and_reports_missing(tmp_path):
    plain = tmp_path / "file"
    encrypted = tmp_path / "file.gear"
    plain.write_bytes(b"plain")
    encrypted.write_bytes(b"encrypted")
    assert gearshift.remove(encrypted.as_posix()) is None
    assert not plain.exists()
    assert not encrypted.exists()
    with pytest.raises(FileNotFoundError, match="No such file"):
        gearshift.remove(plain.as_posix())


def test_ensure_crypt_creates_and_honors_lazy_and_required(tmp_path, test_context):
    gearshift.context.GearshiftContext._instance = test_context
    plain = tmp_path / "file"
    plain.write_bytes(b"payload")

    result = gearshift.ensure_crypt(plain.as_posix() + ".gear")
    assert isinstance(result, gearshift.EnsureResult)
    assert is_dataclass(result)
    assert result.__dict__ == {
        "crypt_name": plain.as_posix() + ".gear",
        "decrypt_name": plain.as_posix(),
        "created": True,
        "cleanup": False,
    }
    assert plain.read_bytes() == b"payload"

    lazy = gearshift.ensure_crypt(plain.as_posix())
    assert lazy.created is False
    missing = gearshift.ensure_crypt((tmp_path / "missing").as_posix(), required=False)
    assert missing.created is False
    with pytest.raises(FileNotFoundError, match="ensure_crypt: No such file"):
        gearshift.ensure_crypt((tmp_path / "required").as_posix())


def test_ensure_crypt_can_replace_existing_encrypted_file(tmp_path, test_context):
    gearshift.context.GearshiftContext._instance = test_context
    plain = tmp_path / "file"
    plain.write_bytes(b"new")
    (tmp_path / "file.gear").write_bytes(b"old")
    result = gearshift.ensure_crypt(plain.as_posix(), lazy=False)
    assert result.created is True
    assert result.cleanup is False
    assert plain.read_bytes() == b"new"
    with gearshift.open(plain.as_posix(), "rb", context=test_context) as source:
        assert source.read() == b"new"


def test_ensure_crypt_cleanup_removes_plaintext(tmp_path, test_context):
    gearshift.context.GearshiftContext._instance = test_context
    plain = tmp_path / "file"
    plain.write_bytes(b"payload")

    result = gearshift.ensure_crypt(plain.as_posix(), cleanup=True)
    assert result.created is True
    assert result.cleanup is True
    assert not plain.exists()


def test_ensure_crypt_cleanup_handles_lazy_and_failed_removal(tmp_path, monkeypatch, test_context):
    gearshift.context.GearshiftContext._instance = test_context
    plain = tmp_path / "file"
    plain.write_bytes(b"payload")
    gearshift.ensure_crypt(plain.as_posix())

    result = gearshift.ensure_crypt(plain.as_posix(), cleanup=True)
    assert result.created is False
    assert result.cleanup is True
    assert not plain.exists()

    plain.write_bytes(b"new plaintext")
    monkeypatch.setattr(gearshift_io.os, "remove", Mock(side_effect=PermissionError))
    result = gearshift.ensure_crypt(plain.as_posix(), cleanup=True)
    assert result.created is False
    assert result.cleanup is False
    assert plain.exists()


def test_ensure_crypt_cleanup_is_complete_when_plaintext_is_already_absent(tmp_path, test_context):
    gearshift.context.GearshiftContext._instance = test_context
    plain = tmp_path / "file"
    plain.write_bytes(b"payload")
    gearshift.ensure_crypt(plain.as_posix(), cleanup=True)

    result = gearshift.ensure_crypt(plain.as_posix(), cleanup=True)
    assert result.created is False
    assert result.cleanup is True


def test_ensure_decrypt_lazy_and_missing_branches(tmp_path):
    plain = tmp_path / "file"
    plain.write_bytes(b"existing")
    result = gearshift.ensure_decrypt(plain.as_posix() + ".gear")
    assert isinstance(result, gearshift.EnsureResult)
    assert is_dataclass(result)
    assert result.cleanup is None
    assert result.created is False

    plain.unlink()
    result = gearshift.ensure_decrypt(plain.as_posix(), required=False)
    assert result.created is False
    with pytest.raises(FileNotFoundError, match="ensure_decrypt: No such file"):
        gearshift.ensure_decrypt(plain.as_posix())


def test_ensure_decrypt_materializes_plaintext(tmp_path, test_context):
    gearshift.context.GearshiftContext._instance = test_context
    plain = tmp_path / "file"
    with gearshift.open(plain.as_posix(), "wb", context=test_context) as output:
        output.write(b"payload")

    result = gearshift.ensure_decrypt(plain.as_posix(), lazy=False)
    assert result.created is True
    assert plain.read_bytes() == b"payload"


def test_encryption_failure_removes_temporary_file(tmp_path):
    context = Mock()
    context.aes_encrypt_to_stream.side_effect = RuntimeError("encryption failed")
    stream = gearshift.Gearshift((tmp_path / "file").as_posix(), "wb", context=context)

    with pytest.raises(RuntimeError, match="encryption failed"):
        with stream as output:
            output.write(b"payload")

    assert stream.filename_tmp is None
    assert not (tmp_path / "file.gear").exists()
