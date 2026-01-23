import pytest

from templisafe.settings.source.source_settings import (
    SourceSettings,
    SourceKind,
)
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.settings_error import SettingsError

# -----------------------------
# Fixtures / example configs
# -----------------------------
HTTP_CONFIG_DICT = {
    "kind": "http",
    "url": "https://api.example.com/data.json",
}

HTTP_YAML = """
kind: http
url: "https://api.example.com/data.json"
"""

HTTP_JSON = '{"kind": "http", "url": "https://api.example.com/data.json"}'


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_http_from_dict():
    instance = SourceSettings.create(**HTTP_CONFIG_DICT)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.kind == SourceKind.HTTP
    assert instance.url == "https://api.example.com/data.json"


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_http():
    instance = HttpSourceSettings.from_dict(HTTP_CONFIG_DICT)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.url == "https://api.example.com/data.json"


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_http():
    instance = HttpSourceSettings.from_yaml(HTTP_YAML)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.url == "https://api.example.com/data.json"


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_http():
    instance = HttpSourceSettings.from_json(HTTP_JSON)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.url == "https://api.example.com/data.json"
