import pytest
import json
import yaml

from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.exceptions.settings_error import SettingsError


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def valid_dict():
    return {"index_key": "my_index"}


@pytest.fixture
def valid_yaml(valid_dict):
    return yaml.safe_dump(valid_dict)


@pytest.fixture
def valid_json(valid_dict):
    return json.dumps(valid_dict)


# -----------------------------
# create(**kwargs)
# -----------------------------
def test_create_with_valid_dict(valid_dict):
    settings = CompilerSettings.create(**valid_dict)
    assert isinstance(settings, CompilerSettings)
    assert settings.index_key == valid_dict["index_key"]


def test_create_missing_index_key_raises():
    with pytest.raises(ValueError, match="Missing 'index_key' field"):
        CompilerSettings.create()


def test_create_invalid_type_raises():
    with pytest.raises(ValueError):
        CompilerSettings.create(index_key=None)


# -----------------------------
# from_dict
# -----------------------------
def test_from_dict_valid(valid_dict):
    settings = CompilerSettings.from_dict(valid_dict)
    assert isinstance(settings, CompilerSettings)
    assert settings.index_key == valid_dict["index_key"]


def test_from_dict_invalid_type():
    with pytest.raises(SettingsError):
        CompilerSettings.from_dict(None)  # type: ignore


# -----------------------------
# from_yaml
# -----------------------------
def test_from_yaml_valid(valid_yaml, valid_dict):
    settings = CompilerSettings.from_yaml(valid_yaml)
    assert isinstance(settings, CompilerSettings)
    assert settings.index_key == valid_dict["index_key"]


def test_from_yaml_invalid_yaml():
    invalid_yaml = "index_key: [unclosed_list"
    with pytest.raises(SettingsError):
        CompilerSettings.from_yaml(invalid_yaml)


def test_from_yaml_not_mapping():
    yaml_str = "- not a mapping"
    with pytest.raises(SettingsError):
        CompilerSettings.from_yaml(yaml_str)


# -----------------------------
# from_json
# -----------------------------
def test_from_json_valid(valid_json, valid_dict):
    settings = CompilerSettings.from_json(valid_json)
    assert isinstance(settings, CompilerSettings)
    assert settings.index_key == valid_dict["index_key"]


def test_from_json_invalid_json():
    invalid_json = '{"index_key": "my_index"'  # missing closing brace
    with pytest.raises(SettingsError):
        CompilerSettings.from_json(invalid_json)


def test_from_json_not_mapping():
    json_str = '["not", "a", "dict"]'
    with pytest.raises(SettingsError):
        CompilerSettings.from_json(json_str)
