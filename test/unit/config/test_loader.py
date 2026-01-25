import pytest

from templisafe.exceptions.config_error import ConfigError
from templisafe.config.config_loader import *


def test_loader_is_abstract():
    with pytest.raises(TypeError):
        ConfigLoader()        # type: ignore

# -----------------
# YAML Loader
# -----------------

def test_yaml_loader_mapping():
    raw = """
    a: 1
    b:
      c: 2
    """

    loader = YamlConfigLoader()
    config: Config = loader.load(raw)

    assert config == {"a": 1, "b": {"c": 2}}

def test_yaml_loader_list():
    raw = """
    - a: 1
    - b:
        c: 2
    """

    loader = YamlConfigLoader()
    config: Config = loader.load(raw)

    assert config == [{"a": 1}, {"b": {"c": 2}}]


def test_yaml_loader_invalid_yaml():
    raw = """
    a: 1
      b: 2
    """

    loader = YamlConfigLoader()

    with pytest.raises(ConfigError):
        loader.load(raw)


# -----------------
# JSON Loader
# -----------------

def test_json_loader_object():
    raw = '{"a": 1, "b": {"c": 2}}'

    loader = JsonConfigLoader()
    config = loader.load(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_json_loader_list():
    raw = '[1, 2, 3]'

    loader = JsonConfigLoader()

    config = loader.load(raw)
    assert config == [1, 2, 3]


def test_json_loader_invalid_json():
    raw = '{"a": 1,}'

    loader = JsonConfigLoader()

    with pytest.raises(ConfigError):
        loader.load(raw)


# -----------------
# TOML Loader
# -----------------

def test_toml_loader_object():
    raw = """
    a = 1

    [b]
    c = 2
    """

    loader = TomlConfigLoader()
    config = loader.load(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_toml_loader_invalid_toml():
    raw = """
    a = 1
    b =
    """

    loader = TomlConfigLoader()

    with pytest.raises(ConfigError):
        loader.load(raw)


def test_toml_loader_missing_dependency(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name in {"tomllib", "tomli"}:
            raise ModuleNotFoundError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    loader = TomlConfigLoader()

    with pytest.raises(ConfigError):
        loader.load("a = 1")


# -----------------
# XML Loader
# -----------------

def test_xml_loader_mapping():
    raw = """
    <root>
        <a>1</a>
        <b>
            <c>2</c>
        </b>
    </root>
    """

    loader = XmlConfigLoader()
    config: Config = loader.load(raw)

    assert config == {
        "root": {
            "a": "1",
            "b": {
                "c": "2"
            }
        }
    }


def test_xml_loader_list():
    raw = """
    <root>
        <item>
            <a>1</a>
        </item>
        <item>
            <b>2</b>
        </item>
    </root>
    """

    loader = XmlConfigLoader()
    config: Config = loader.load(raw)

    assert config == {
        "root": { 
            "item": [
                {"a": "1"},
                {"b": "2"},
            ]
        }
    }


def test_xml_loader_invalid_xml():
    raw = """
    <root>
        <a>1</b>
    </root>
    """

    loader = XmlConfigLoader()

    with pytest.raises(ConfigError):
        loader.load(raw)

