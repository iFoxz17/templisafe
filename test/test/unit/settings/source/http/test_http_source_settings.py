import pytest

from templisafe.settings.source.http.http_async_session_settings import (
    HttpAsyncSessionSettings,
    HttpSyncSessionSettings,
)
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings

# -----------------------------
# Fixtures / example configs
# -----------------------------
HTTP_CONFIG_DICT = {
    "kind": "http",
    "url": "https://api.example.com/data.json",
}

HTTP_CONFIG_DICT_FULL = {
    "kind": "http",
    "url": "https://api.example.com/data.json",
    "timeout": 10,
    "sync_session_settings": {},
    "async_session_settings": {
        "max_connections": 200,
        "max_connections_per_host": 50,
        "force_close": True,
        "ttl_dns_cache": 120,
    },
}

HTTP_YAML = """
kind: http
url: "https://api.example.com/data.json"
timeout: 10
async_session_settings:
  max_connections: 200
  max_connections_per_host: 50
  force_close: true
  ttl_dns_cache: 120
"""

HTTP_JSON = """
{
    "kind": "http",
    "url": "https://api.example.com/data.json",
    "timeout": 10,
    "async_session_settings": {
        "max_connections": 200,
        "max_connections_per_host": 50,
        "force_close": true,
        "ttl_dns_cache": 120
    }
}
"""


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_http_source_from_dict():
    instance = SourceSettings.create(**HTTP_CONFIG_DICT)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.kind == SourceKind.HTTP
    assert instance.url == "https://api.example.com/data.json"


def test_create_http_source_with_full_config():
    instance = SourceSettings.create(**HTTP_CONFIG_DICT_FULL)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.timeout == 10
    assert isinstance(instance.sync_session_settings, HttpSyncSessionSettings)
    assert isinstance(instance.async_session_settings, HttpAsyncSessionSettings)
    assert instance.async_session_settings.max_connections == 200


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_http_source():
    instance = HttpSourceSettings.from_dict(HTTP_CONFIG_DICT)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.url == "https://api.example.com/data.json"
    assert instance.timeout == 30  # default
    assert isinstance(instance.sync_session_settings, HttpSyncSessionSettings)
    assert isinstance(instance.async_session_settings, HttpAsyncSessionSettings)


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_http_source():
    instance = HttpSourceSettings.from_yaml(HTTP_YAML)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.url == "https://api.example.com/data.json"
    assert instance.timeout == 10
    assert instance.async_session_settings.force_close is True
    assert instance.async_session_settings.ttl_dns_cache == 120


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_http_source():
    instance = HttpSourceSettings.from_json(HTTP_JSON)
    assert isinstance(instance, HttpSourceSettings)
    assert instance.url == "https://api.example.com/data.json"
    assert instance.timeout == 10
    assert instance.async_session_settings.max_connections_per_host == 50


# -----------------------------
# Validation tests
# -----------------------------
def test_http_source_requires_url():
    with pytest.raises(ValueError):
        HttpSourceSettings.from_dict({"kind": "http"})


def test_http_source_timeout_must_be_positive():
    with pytest.raises(ValueError):
        HttpSourceSettings.from_dict(
            {
                "kind": "http",
                "url": "https://api.example.com/data.json",
                "timeout": 0,
            }
        )


def test_http_source_invalid_async_session_settings():
    with pytest.raises(ValueError):
        HttpSourceSettings.from_dict(
            {
                "kind": "http",
                "url": "https://api.example.com/data.json",
                "async_session_settings": {
                    "max_connections": -1,
                },
            }
        )
