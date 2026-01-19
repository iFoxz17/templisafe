import pytest

from templisafe.settings.source.source_settings import (
    SourceSettings,
    SourceKind,
)
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.exceptions.settings_error import SettingsError

# -----------------------------
# Fixtures / example configs
# -----------------------------
INLINE_CONFIG_DICT = {"kind": "inline", "content": "SELECT 1"}

INLINE_YAML = """
kind: inline
content: "SELECT 1"
"""

INLINE_JSON = '{"kind": "inline", "content": "SELECT 1"}'


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_inline_from_dict():
    instance = SourceSettings.create(**INLINE_CONFIG_DICT)
    assert isinstance(instance, InlineSourceSettings)
    assert instance.kind == SourceKind.INLINE
    assert instance.content == "SELECT 1"

def test_create_invalid_kind_raises():
    with pytest.raises(ValueError, match="Invalid kind: 'invalid'"):
        SourceSettings.create(kind="invalid")

def test_create_missing_kind_raises():
    with pytest.raises(ValueError, match="Missing 'kind'"):
        SourceSettings.create()

def test_create_invalid_field_raises():
    # Extra field not allowed
    with pytest.raises(ValueError):
        SourceSettings.create(kind="inline", content="SELECT 1", foo=123)


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_inline():
    instance = InlineSourceSettings.from_dict(INLINE_CONFIG_DICT)
    assert isinstance(instance, InlineSourceSettings)
    assert instance.content == "SELECT 1"


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_inline():
    instance = InlineSourceSettings.from_yaml(INLINE_YAML)
    assert isinstance(instance, InlineSourceSettings)
    assert instance.content == "SELECT 1"

def test_from_yaml_invalid_yaml_raises():
    invalid_yaml = "this: [unbalanced"
    with pytest.raises(SettingsError):
        InlineSourceSettings.from_yaml(invalid_yaml)

def test_from_yaml_not_a_dict_raises():
    yaml_list = "- item1\n- item2"
    with pytest.raises(SettingsError):
        InlineSourceSettings.from_yaml(yaml_list)


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_inline():
    instance = InlineSourceSettings.from_json(INLINE_JSON)
    assert isinstance(instance, InlineSourceSettings)
    assert instance.content == "SELECT 1"

def test_from_json_invalid_json_raises():
    invalid_json = '{"foo": "bar",}'
    with pytest.raises(SettingsError):
        InlineSourceSettings.from_json(invalid_json)

def test_from_json_not_a_dict_raises():
    json_list = '["a", "b"]'
    with pytest.raises(SettingsError):
        InlineSourceSettings.from_json(json_list)
