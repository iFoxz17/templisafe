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


def test_from_dict():
    settings = DummySettings.from_dict(DICT_CONFIG)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "dict"
    assert settings.bar == 123


def test_invalid_yaml():
    invalid_yaml = "::: Not a valid yaml:::"  # bar should be int
    with pytest.raises(SettingsError):
        DummySettings.from_yaml(invalid_yaml)


def test_invalid_json():
    invalid_json = '::: Not a valid json:::'  # bar missing
    with pytest.raises(SettingsError):
        DummySettings.from_json(invalid_json)


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
