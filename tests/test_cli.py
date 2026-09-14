import json
import os
from unittest.mock import Mock, call

import click

from gearshift.context import GearshiftContext
from scripts import gs


def invoke_cli_callback(cfg=None, updates=()):
    with click.Context(gs.cli):
        gs.cli.callback(False, cfg, updates)


def test_named_config_adds_yaml_suffix(monkeypatch):
    context = Mock()
    instance = Mock(return_value=context)
    expanded = Mock(return_value="/resolved/named.yaml")
    monkeypatch.setattr(GearshiftContext, "instance", instance)
    monkeypatch.setattr(gs.os.path, "expanduser", expanded)
    monkeypatch.setenv("GEARSHIFT_SET", "original")

    invoke_cli_callback("named")

    expanded.assert_called_once_with("~/.gearshift/named.yaml")
    instance.assert_called_once_with(cfg_file="/resolved/named.yaml", cfg_optional=False)


def test_cli_preserves_config_paths_and_applies_updates(monkeypatch):
    context = Mock()
    instance = Mock(return_value=context)
    monkeypatch.setattr(GearshiftContext, "instance", instance)
    monkeypatch.setenv("GEARSHIFT_SET", "original")

    invoke_cli_callback("config/custom.yaml", ("workers=3", "label=blue"))

    instance.assert_called_once_with(cfg_file="config/custom.yaml", cfg_optional=False)
    assert context.set.call_args_list == [call("workers", 3), call("label", "blue")]
    assert json.loads(os.environ["GEARSHIFT_SET"]) == {"workers": 3, "label": "blue"}
