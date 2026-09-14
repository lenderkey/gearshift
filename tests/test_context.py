import base64
import io
import json
import os
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import hvac
import pytest

import gearshift.context as context_module
from gearshift.context import GearshiftContext, GearshiftNoContextError
from gearshift.helpers import sha256_data


def test_context_loads_yaml_and_handles_missing_config(tmp_path):
    config = tmp_path / "gearshift.yaml"
    config.write_text("src:\n  root: ./files\n", encoding="utf-8")
    context = GearshiftContext(cfg_file=str(config))
    assert context.cfg == {"src": {"root": "./files"}}

    config.write_text("", encoding="utf-8")
    assert GearshiftContext(cfg_file=str(config)).cfg == {}
    assert GearshiftContext(cfg_file=str(tmp_path / "missing"), cfg_optional=True).cfg == {}
    with pytest.raises(GearshiftNoContextError, match="not found"):
        GearshiftContext(cfg_file=str(tmp_path / "missing"))


def test_context_singleton_can_be_reused_and_replaced():
    first = GearshiftContext.instance(cfg={"value": 1})
    assert GearshiftContext.instance() is first
    second = GearshiftContext.instance(replace_instance=True, cfg={"value": 2})
    assert second is not first
    assert second.cfg == {"value": 2}


def test_source_properties_and_paths(tmp_path):
    config = tmp_path / "config" / "gearshift.yaml"
    context = GearshiftContext(
        cfg_file=str(config),
        cfg={
            "src": {
                "root": "./source",
                "host": "example.com",
                "url": "ssh://example.com/source",
                "user": "alice",
                "folder": "nested",
                "pem": "key.pem",
                "token_id": "token",
            }
        },
    )
    source_root = os.path.normpath(str(config.parent / "source"))
    assert context.src_root == source_root
    assert context.src_host == "example.com"
    assert context.src_url == "ssh://example.com/source"
    assert context.src_user == "alice"
    assert context.src_folder == "nested"
    assert context.src_pem == "key.pem"
    assert context.src_token_id == "token"
    assert context.src_path("file.txt") == os.path.join(source_root, "file.txt")
    assert context.dst_link_path("hash", "abcdef") == os.path.join(source_root, ".links", "hash", "ab", "cd", "abcdef")
    assert context.dst_link_path(None, "abcdef").endswith("/.links/plaintext/ab/cd/abcdef")
    assert context.dst_store_path("nested/file") == os.path.join(source_root, "nested", "file")
    with pytest.raises(ValueError, match="must stay within"):
        context.dst_store_path("../outside")

    context.set("src.folder", None)
    assert context.src_folder == "/"
    context.set("new.value", 3)
    assert context.get("new.value") == 3


def test_resolve_path_variants_and_missing_path(tmp_path, monkeypatch):
    context = GearshiftContext(cfg_file=str(tmp_path / "gearshift.yaml"), cfg={})
    monkeypatch.setattr(context_module.os.path, "expanduser", lambda value: value.replace("~", "/home/test", 1))
    assert context.resolve_path("~/keys") == "/home/test/keys"
    assert context.resolve_path("./keys") == os.path.normpath(str(tmp_path / "keys"))
    assert context.resolve_path("/absolute/keys") == "/absolute/keys"
    with pytest.raises(SystemExit) as exc_info:
        context.resolve_path(None)
    assert exc_info.value.code == 1


def test_dst_has_hash_accepts_a_data_hash(tmp_path):
    context = GearshiftContext(cfg={"src": {"root": str(tmp_path)}})
    assert context.dst_has_hash("abcdef") is False


def test_dst_has_hash_uses_resolved_link_path(monkeypatch):
    context = GearshiftContext(cfg={})
    context.dst_link_path = Mock(return_value="/links/hash")
    monkeypatch.setattr(context_module.os.path, "exists", lambda value: value == "/links/hash")
    assert context.dst_has_hash("abcdef") is True


def test_ingest_link_rejects_absolute_and_returns_false_for_missing(monkeypatch):
    context = GearshiftContext(cfg={})
    with pytest.raises(ValueError, match="must be relative"):
        context.ingest_link("abcdef", "/absolute")

    context.dst_link_path = Mock(return_value="/links/hash")
    monkeypatch.setattr(context_module.os.path, "exists", lambda _value: False)
    assert context.ingest_link("abcdef", "relative") is False


def test_ingest_link_creates_and_reuses_hard_links(tmp_path):
    context = GearshiftContext(cfg={})
    link = tmp_path / "links" / "hash"
    link.parent.mkdir()
    link.write_bytes(b"data")
    destination = tmp_path / "store" / "nested" / "file"
    context.dst_link_path = Mock(return_value=str(link))
    context.dst_store_path = Mock(return_value=str(destination))

    assert context.ingest_link("abcdef", "nested/file") is True
    assert os.stat(link).st_ino == os.stat(destination).st_ino
    assert context.ingest_link("abcdef", "nested/file") is True


def test_ingest_link_replaces_existing_destination(tmp_path):
    context = GearshiftContext(cfg={})
    link = tmp_path / "link"
    link.write_bytes(b"new")
    destination = tmp_path / "destination"
    destination.write_bytes(b"old")
    context.dst_link_path = Mock(return_value=str(link))
    context.dst_store_path = Mock(return_value=str(destination))

    assert context.ingest_link("abcdef", "destination") is True
    assert destination.read_bytes() == b"new"
    assert os.stat(link).st_ino == os.stat(destination).st_ino


def test_ingest_link_ignores_remove_errors(monkeypatch):
    context = GearshiftContext(cfg={})
    context.dst_link_path = Mock(return_value="link")
    context.dst_store_path = Mock(return_value="destination")
    stats = {"link": SimpleNamespace(st_ino=1), "destination": SimpleNamespace(st_ino=2)}
    monkeypatch.setattr(context_module.os.path, "exists", lambda _value: True)
    monkeypatch.setattr(context_module.os, "stat", lambda value: stats[value])
    monkeypatch.setattr(context_module.os, "remove", Mock(side_effect=OSError))
    monkeypatch.setattr(context_module.os, "makedirs", Mock())
    link_mock = Mock()
    monkeypatch.setattr(context_module.os, "link", link_mock)

    assert context.ingest_link("abcdef", "destination") is True
    link_mock.assert_called_once_with("link", "destination")


def test_server_key_test_and_unknown_system():
    context = GearshiftContext(cfg={"security": {"key_system": "test", "key_hash": "configured"}})
    assert context.server_key_hash() == "configured"
    key, key_hash = context.server_key("ignored")
    assert key == b"0" * 32
    assert key_hash == "testkeyhash"

    context.set("security.key_system", "mystery")
    with pytest.raises(ValueError, match="unknown key_system"):
        context.server_key()


def test_server_key_from_filesystem(tmp_path):
    first = base64.urlsafe_b64encode(b"1" * 32)
    selected = base64.urlsafe_b64encode(b"2" * 32)
    keys = tmp_path / "keys"
    keys.write_bytes(first + b"\n" + selected)
    selected_hash = sha256_data(selected)
    context = GearshiftContext(cfg={"security": {"key_system": "fs", "key_file": str(keys), "key_hash": selected_hash}})

    assert context.server_key() == (b"2" * 32, selected_hash)
    assert context.server_key(selected_hash) == (b"2" * 32, selected_hash)
    with pytest.raises(ValueError, match="has no key"):
        context.server_key("missing")


def vault_client(response=None, error=None):
    reader = Mock(return_value=response, side_effect=error)
    client = SimpleNamespace(secrets=SimpleNamespace(kv=SimpleNamespace(v2=SimpleNamespace(read_secret=reader))))
    return client, reader


def test_server_key_from_vault(monkeypatch):
    encoded = base64.urlsafe_b64encode(b"v" * 32).decode()
    client, reader = vault_client({"data": {"data": {"key": encoded, "key_hash": "vault-hash"}}})
    context = GearshiftContext(cfg={"security": {"key_system": "vault"}, "vault": {"key_group": "team"}})
    monkeypatch.setattr(context, "get_vault_client", lambda: client)

    assert context.server_key() == (b"v" * 32, "vault-hash")
    reader.assert_called_once_with(path="gearshift-keys/team/current")

    empty_client, _ = vault_client({"data": {"data": {"key": "", "key_hash": "vault-hash"}}})
    monkeypatch.setattr(context, "get_vault_client", lambda: empty_client)
    with pytest.raises(KeyError, match=r"\[2\]"):
        context.server_key("missing")

    decoded_empty_client, _ = vault_client({"data": {"data": {"key": "====", "key_hash": "vault-hash"}}})
    monkeypatch.setattr(context, "get_vault_client", lambda: decoded_empty_client)
    with pytest.raises(KeyError, match=r"\[2\]"):
        context.server_key("empty")


def test_server_key_reports_missing_vault_key(monkeypatch):
    client, _ = vault_client({})
    context = GearshiftContext(cfg={"security": {"key_system": "vault"}})
    monkeypatch.setattr(context, "get_vault_client", lambda: client)
    with pytest.raises(KeyError, match="key not found"):
        context.server_key("missing")


def test_server_key_translates_vault_missing_path(monkeypatch):
    class InvalidPathError(Exception):
        pass

    client, _ = vault_client(error=InvalidPathError())
    context = GearshiftContext(cfg={"security": {"key_system": "vault"}})
    monkeypatch.setattr(context, "get_vault_client", lambda: client)
    monkeypatch.setattr(
        context_module,
        "hvac",
        SimpleNamespace(exceptions=SimpleNamespace(InvalidPath=InvalidPathError)),
    )
    with pytest.raises(KeyError, match="gearshift-keys/default/missing"):
        context.server_key("missing")


def test_server_key_translates_real_vault_missing_path(monkeypatch):
    client, _ = vault_client(error=hvac.exceptions.InvalidPath())
    context = GearshiftContext(cfg={"security": {"key_system": "vault"}})
    monkeypatch.setattr(context, "get_vault_client", lambda: client)
    with pytest.raises(KeyError, match="key not found"):
        context.server_key("missing")


def install_fake_aws(monkeypatch, response=None, error=None):
    client = Mock()
    client.get_secret_value = Mock(return_value=response, side_effect=error)
    session = Mock()
    session.client.return_value = client
    boto3 = ModuleType("boto3")
    boto3.session = SimpleNamespace(Session=Mock(return_value=session))
    exceptions = ModuleType("botocore.exceptions")

    class ClientError(Exception):
        pass

    exceptions.ClientError = ClientError
    botocore = ModuleType("botocore")
    botocore.exceptions = exceptions
    monkeypatch.setitem(sys.modules, "boto3", boto3)
    monkeypatch.setitem(sys.modules, "botocore", botocore)
    monkeypatch.setitem(sys.modules, "botocore.exceptions", exceptions)
    return boto3, session, client, ClientError


@pytest.mark.parametrize("double_encoded", [False, True])
def test_server_key_from_aws(monkeypatch, double_encoded):
    raw_key = b"a" * 32
    encoded = base64.urlsafe_b64encode(raw_key)
    if double_encoded:
        encoded = base64.urlsafe_b64encode(encoded)
    boto3, session, client, _ = install_fake_aws(
        monkeypatch, response={"SecretString": json.dumps({"key-hash": encoded.decode()})}
    )
    context = GearshiftContext(
        cfg={
            "security": {
                "key_system": "aws",
                "key_hash": "key-hash",
                "secret_name": "secret",
                "aws_access_key_id": "access",
                "aws_secret_access_key": "secret-key",
                "region_name": "us-east-1",
                "profile_name": "profile",
            }
        }
    )

    assert context.server_key() == (raw_key, "key-hash")
    boto3.session.Session.assert_called_once_with(profile_name="profile")
    session.client.assert_called_once_with(
        service_name="secretsmanager",
        region_name="us-east-1",
        aws_access_key_id="access",
        aws_secret_access_key="secret-key",
    )
    client.get_secret_value.assert_called_once_with(SecretId="secret")


def test_server_key_aws_errors(monkeypatch):
    _, _, client, client_error = install_fake_aws(monkeypatch, response={"SecretString": "{}"})
    context = GearshiftContext(cfg={"security": {"key_system": "aws", "key_hash": "missing", "secret_name": "secret"}})
    with pytest.raises(KeyError, match="key not found"):
        context.server_key()

    client.get_secret_value.side_effect = client_error("failure")
    with pytest.raises(client_error, match="failure"):
        context.server_key("missing")


def test_encrypted_stream_round_trip_and_metadata(test_context):
    output = io.BytesIO()
    assert test_context.aes_encrypt_to_stream(b"payload", output) is None
    encrypted = output.getvalue()
    assert encrypted.startswith(b"GEARH\x0btestkeyhashI\x0c")
    assert test_context.aes_decrypt_to_bytes(io.BytesIO(encrypted)) == b"payload"


def test_decrypt_rejects_invalid_or_incomplete_headers(test_context):
    with pytest.raises(ValueError, match="invalid header"):
        test_context.aes_decrypt_to_bytes(io.BytesIO(b"NOPE"))

    key = b"H\x0btestkeyhash"
    iv = b"I\x0c" + b"i" * 12
    tag = b"T\x10" + b"t" * 16
    end = b"\0\0"
    for stream in (key + tag + end, key + iv + end, iv + tag + end):
        with pytest.raises(ValueError, match="missing"):
            test_context.aes_decrypt_to_bytes(io.BytesIO(b"GEAR" + stream))

    with pytest.raises(ValueError, match="missing block length"):
        test_context.aes_decrypt_to_bytes(io.BytesIO(b"GEARH"))
    with pytest.raises(ValueError, match="incomplete block"):
        test_context.aes_decrypt_to_bytes(io.BytesIO(b"GEARH\x03ab"))
    with pytest.raises(ValueError, match="end block must be empty"):
        test_context.aes_decrypt_to_bytes(io.BytesIO(b"GEAR\0\x01x"))


def test_decrypt_stops_if_stream_returns_none(test_context):
    stream = Mock()
    stream.read.side_effect = [b"GEAR", None]
    with pytest.raises(ValueError, match="unexpected end"):
        test_context.aes_decrypt_to_bytes(stream)


def test_decrypt_stops_at_normal_stream_eof(test_context):
    with pytest.raises(ValueError, match="unexpected end"):
        test_context.aes_decrypt_to_bytes(io.BytesIO(b"GEAR"))


def test_decrypt_handles_optional_and_rejects_required_unknown_blocks(test_context):
    output = io.BytesIO()
    test_context.aes_encrypt_to_stream(b"payload", output)
    encrypted = output.getvalue()
    with_optional = encrypted[:4] + b"x\x00" + encrypted[4:]
    assert test_context.aes_decrypt_to_bytes(io.BytesIO(with_optional)) == b"payload"
    with pytest.raises(ValueError, match=r"unknown \(required\) block"):
        test_context.aes_decrypt_to_bytes(io.BytesIO(encrypted[:4] + b"Q\x00" + encrypted[4:]))


def test_decrypt_skips_optional_block_payload(test_context):
    output = io.BytesIO()
    test_context.aes_encrypt_to_stream(b"payload", output)
    encrypted = output.getvalue()
    with_optional = encrypted[:4] + b"x\x03abc" + encrypted[4:]
    assert test_context.aes_decrypt_to_bytes(io.BytesIO(with_optional)) == b"payload"


def test_decrypt_optional_block_without_patching_runtime(test_context):
    output = io.BytesIO()
    test_context.aes_encrypt_to_stream(b"payload", output)
    encrypted = output.getvalue()
    with_optional = encrypted[:4] + b"x\x00" + encrypted[4:]
    assert test_context.aes_decrypt_to_bytes(io.BytesIO(with_optional)) == b"payload"


def test_vault_helpers(monkeypatch):
    context = GearshiftContext(cfg={})
    assert context.get_vault_key_root() == "gearshift-keys"
    assert context.get_vault_key_group() == "default"
    context.set("vault.key_group", "team")
    assert context.get_vault_key_group() == "team"

    authenticated = Mock()
    authenticated.is_authenticated.return_value = True
    monkeypatch.setattr("hvac.Client", Mock(return_value=authenticated))
    assert context.get_vault_client() is authenticated

    unauthenticated = Mock()
    unauthenticated.is_authenticated.return_value = False
    monkeypatch.setattr("hvac.Client", Mock(return_value=unauthenticated))
    with pytest.raises(PermissionError, match="Authentication failed"):
        context.get_vault_client()
