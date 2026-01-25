import pytest

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.renderer_settings import RendererSettings, Settings


# -----------------------------
# Fixtures / example configs
# -----------------------------
RENDERER_DICT = {"index_key": "idx"}
RENDERER_YAML = """
index_key: idx
"""

INVALID_YAML = "index_key: [unbalanced"
YAML_NOT_DICT = "- item1\n- item2"


# -----------------------------
# Tests for create()
# -----------------------------

def test_create_base_with_valid_dict():
    instance = Settings.create(kind="renderer_settings", index_key="idx")
    assert isinstance(instance, RendererSettings)
    assert instance.index_key == "idx"

def test_create_success():
    instance = RendererSettings.create(index_key="idx")
    assert isinstance(instance, RendererSettings)
    assert instance.index_key == "idx"

def test_create_missing_index_key_raises():
    with pytest.raises(SettingsError):
        RendererSettings.create()

def test_create_invalid_field_raises():
    with pytest.raises(SettingsError):
        RendererSettings.create(index_key="idx", extra="not_allowed")


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_success():
    instance = RendererSettings.from_yaml(RENDERER_YAML)
    assert isinstance(instance, RendererSettings)
    assert instance.index_key == "idx"

def test_from_yaml_invalid_yaml_raises():
    with pytest.raises(SettingsError):
        RendererSettings.from_yaml(INVALID_YAML)

def test_from_yaml_not_a_dict_raises():
    with pytest.raises(SettingsError):
        RendererSettings.from_yaml(YAML_NOT_DICT)

def test_from_yaml_invalid_fields_raises():
    bad_yaml = "::: Not a yaml :::"
    with pytest.raises(SettingsError):
        RendererSettings.from_yaml(bad_yaml)
