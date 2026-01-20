from pydantic import ConfigDict
import pytest
from typing import Any

from templisafe.source.source import Source
from templisafe.settings.settings import Settings
from templisafe.loader.loader import *
from templisafe.util.util import ContentType
from templisafe.exceptions.load_error import UnsopportedLoadError
from templisafe.resolver.config_loader import ConfigLoader


# --- Dummy Settings class for testing ---
class DummySettings(Settings):
    foo: str
    bar: int

    @classmethod
    def _parse_config(cls, config: dict[str, Any]) -> "DummySettings":
        return cls.model_validate(config)
    
class DummySettingsXml(Settings):
    foo: str
    bar: int

    @classmethod
    def _parse_config(cls, config: dict[str, Any]) -> "DummySettingsXml":
        return cls.model_validate(config['settings'])


# --- Helper to create fake Source objects ---
class FakeSource(Source):
    def __init__(self, content_type: ContentType, raw: str):
        self._content_type = content_type
        self._raw = raw

    @property
    def content_type(self) -> ContentType:
        return self._content_type

    def read(self) -> str:
        return self._raw


# --- Sample config strings ---
YAML_RAW = "foo: yaml\nbar: 42"
JSON_RAW = '{"foo": "json", "bar": 99}'
TOML_RAW = """
foo = "toml"
bar = 777
"""
XML_RAW = """
<settings>
    <foo>xml</foo>
    <bar>42</bar>
</settings>
"""
INVALID_RAW = "not a valid format"


# ---------------------------
# Tests
# ---------------------------

def test_yaml_loader_called(monkeypatch):
    loader = ConfigLoader()
    source = FakeSource(ContentType.YAML, YAML_RAW)
    config = loader.load_config(source)
    assert config["foo"] == "yaml"
    assert isinstance(loader._yaml_loader, YamlLoader)


def test_json_loader_called(monkeypatch):
    loader = ConfigLoader()
    source = FakeSource(ContentType.JSON, JSON_RAW)
    config = loader.load_config(source)
    assert config["foo"] == "json"
    assert isinstance(loader._json_loader, JsonLoader)


def test_toml_loader_called(monkeypatch):
    loader = ConfigLoader()
    source = FakeSource(ContentType.TOML, TOML_RAW)
    config = loader.load_config(source)
    assert config["foo"] == "toml"
    assert isinstance(loader._toml_loader, TomlLoader)


def test_xml_loader_called():
    loader = ConfigLoader()
    source = FakeSource(ContentType.XML, XML_RAW)
    config = loader.load_config(source)
    assert config["settings"]["foo"] == "xml"
    assert config["settings"]["bar"] == "42"
    assert isinstance(loader._xml_loader, XmlLoader)


def test_unsupported_content_type_raises():
    loader = ConfigLoader()
    source = FakeSource("unsupported_type", "data")     # type: ignore
    with pytest.raises(UnsopportedLoadError):
        loader.load_config(source)


def test_load_settings_returns_settings_instance(monkeypatch):
    loader = ConfigLoader()
    source = FakeSource(ContentType.YAML, YAML_RAW)

    # Patch Settings.from_dict to DummySettings for testing
    monkeypatch.setattr("templisafe.resolver.config_loader.Settings.from_dict", DummySettings.from_dict)

    settings = loader.load_settings(source)
    assert isinstance(settings, DummySettings)
    assert settings.foo == "yaml"
    assert settings.bar == 42


def test_load_settings_returns_settings_instance_xml(monkeypatch):
    loader = ConfigLoader()
    source = FakeSource(ContentType.XML, XML_RAW)

    # Patch Settings.from_dict to DummySettings for testing
    monkeypatch.setattr("templisafe.resolver.config_loader.Settings.from_dict", DummySettingsXml.from_dict)

    settings = loader.load_settings(source)
    assert isinstance(settings, DummySettingsXml)
    assert settings.foo == "xml"
    assert settings.bar == 42


def test_lazy_initialization():
    loader = ConfigLoader()
    source_yaml = FakeSource(ContentType.YAML, YAML_RAW)
    source_json = FakeSource(ContentType.JSON, JSON_RAW)
    source_toml = FakeSource(ContentType.TOML, TOML_RAW)
    source_xml = FakeSource(ContentType.XML, XML_RAW)

    # Initially loaders are None
    assert loader._yaml_loader is None
    assert loader._json_loader is None
    assert loader._toml_loader is None
    assert loader._xml_loader is None

    loader.load_config(source_yaml)
    assert isinstance(loader._yaml_loader, YamlLoader)
    assert loader._json_loader is None
    assert loader._toml_loader is None
    assert loader._xml_loader is None

    loader.load_config(source_json)
    assert isinstance(loader._json_loader, JsonLoader)

    loader.load_config(source_toml)
    assert isinstance(loader._toml_loader, TomlLoader)

    loader.load_config(source_xml)
    assert isinstance(loader._xml_loader, XmlLoader)
