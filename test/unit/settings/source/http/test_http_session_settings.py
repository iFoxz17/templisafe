import pytest

from templisafe.settings.settings import Settings, SettingsKind
from templisafe.settings.source.http.http_async_session_settings import (
    HttpSyncSessionSettings,
    HttpAsyncSessionSettings,
)
from templisafe.exceptions.settings_error import SettingsError


# -----------------------------
# Fixtures / example configs
# -----------------------------
HTTP_SYNC_CONFIG_DICT = {
    "kind": "http_sync_session_settings",
}

HTTP_ASYNC_CONFIG_DICT = {
    "kind": "http_async_session_settings",
    "max_connections": 500,
    "max_connections_per_host": 100,
    "force_close": True,
    "ttl_dns_cache": 60,
}

HTTP_ASYNC_YAML = """
kind: http_async_session_settings
max_connections: 500
max_connections_per_host: 100
force_close: true
ttl_dns_cache: 60
"""

HTTP_ASYNC_JSON = """
{
    "kind": "http_async_session_settings",
    "max_connections": 500,
    "max_connections_per_host": 100,
    "force_close": true,
    "ttl_dns_cache": 60
}
"""


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_http_sync_session_from_dict():
    instance = Settings.create(**HTTP_SYNC_CONFIG_DICT)
    assert isinstance(instance, HttpSyncSessionSettings)
    #assert instance.kind == SettingsKind.HTTP_SYNC_SESSION_SETTINGS


def test_create_http_async_session_from_dict():
    instance = Settings.create(**HTTP_ASYNC_CONFIG_DICT)
    assert isinstance(instance, HttpAsyncSessionSettings)
    #assert instance.kind == SettingsKind.HTTP_ASYNC_SESSION_SETTINGS
    assert instance.max_connections == 500
    assert instance.max_connections_per_host == 100
    assert instance.force_close is True
    assert instance.ttl_dns_cache == 60


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_http_async_session():
    instance = HttpAsyncSessionSettings.from_dict(HTTP_ASYNC_CONFIG_DICT)
    assert isinstance(instance, HttpAsyncSessionSettings)
    assert instance.max_connections == 500
    assert instance.max_connections_per_host == 100
    assert instance.force_close is True
    assert instance.ttl_dns_cache == 60


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_http_async_session():
    instance = HttpAsyncSessionSettings.from_yaml(HTTP_ASYNC_YAML)
    assert isinstance(instance, HttpAsyncSessionSettings)
    assert instance.max_connections == 500
    assert instance.max_connections_per_host == 100
    assert instance.force_close is True
    assert instance.ttl_dns_cache == 60


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_http_async_session():
    instance = HttpAsyncSessionSettings.from_json(HTTP_ASYNC_JSON)
    assert isinstance(instance, HttpAsyncSessionSettings)
    assert instance.max_connections == 500
    assert instance.max_connections_per_host == 100
    assert instance.force_close is True
    assert instance.ttl_dns_cache == 60


# -----------------------------
# Validation tests
# -----------------------------
@pytest.mark.parametrize(
    "field,value",
    [
        ("max_connections", -1),
        ("max_connections_per_host", -1),
        ("ttl_dns_cache", -1),
    ],
)
def test_http_async_session_validation_errors(field, value):
    bad_config = HTTP_ASYNC_CONFIG_DICT | {field: value}
    with pytest.raises(SettingsError):
        HttpAsyncSessionSettings.from_dict(bad_config)
