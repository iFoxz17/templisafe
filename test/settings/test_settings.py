import pytest
from typing import Dict, Any, Type

from templisafe.settings.settings import Settings, SettingsError

# Concrete subclass for testing
class DummySettings(Settings):
    foo: str
    bar: int

    @classmethod
    def _parse_config(cls: Type["DummySettings"], config: Dict[str, Any]) -> "DummySettings":
        # Simply validate with Pydantic
        return cls.model_validate(config)


# Sample configurations
YAML_CONFIG = """
foo: hello
bar: 42
"""
JSON_CONFIG = '{"foo": "world", "bar": 99}'
TOML_CONFIG = """
foo = "toml"
bar = 777
"""
DICT_CONFIG = {"foo": "dict", "bar": 123}

def test_from_yaml():
    settings = DummySettings.from_yaml(YAML_CONFIG)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "hello"
    assert settings.bar == 42


def test_from_json():
    settings = DummySettings.from_json(JSON_CONFIG)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "world"
    assert settings.bar == 99


def test_from_toml():
    settings = DummySettings.from_toml(TOML_CONFIG)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "toml"
    assert settings.bar == 777


def test_from_dict():
    settings = DummySettings.from_dict(DICT_CONFIG)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "dict"
    assert settings.bar == 123


def test_create_directly_without_kind():
    # Should create a DummySettings instance using the factory directly
    settings = DummySettings.create(foo="direct", bar=555)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "direct"
    assert settings.bar == 555


def test_create_with_invalid_field_raises():
    # Should raise ValueError because 'bar' is required int, not str
    with pytest.raises(ValueError) as excinfo:
        DummySettings.create(foo="oops", bar="not-an-int")
    

def test_invalid_yaml():
    invalid_yaml = "::: Not a valid yaml:::"
    with pytest.raises(SettingsError):
        DummySettings.from_yaml(invalid_yaml)


def test_invalid_json():
    invalid_json = '::: Not a valid json:::'
    with pytest.raises(SettingsError):
        DummySettings.from_json(invalid_json)


def test_invalid_toml():
    invalid_toml = '::: Not a valid toml:::'
    with pytest.raises(SettingsError):
        DummySettings.from_toml(invalid_toml)


def test_non_dict_yaml():
    yaml_list = "- item1\n- item2"
    with pytest.raises(SettingsError):
        DummySettings.from_yaml(yaml_list)


def test_non_dict_json():
    json_list = '["a", "b"]'
    with pytest.raises(SettingsError):
        DummySettings.from_json(json_list)


def test_non_dict_from_dict():
    with pytest.raises(SettingsError):
        DummySettings.from_dict(["not", "a", "dict"])    # type: ignore
