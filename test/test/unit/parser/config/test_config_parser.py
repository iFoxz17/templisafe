import pytest

from templisafe.exceptions.config_error import ConfigError
from templisafe.parser.config.config_parser import *


def test_config_parser_is_abstract():
    with pytest.raises(TypeError):
        ConfigParser()  # type: ignore


# -----------------
# YAML Config_parser
# -----------------


def test_yaml_config_parser_mapping():
    raw = """
    a: 1
    b:
      c: 2
    """

    config_parser = YamlParser()
    config: Config = config_parser.parse(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_yaml_config_parser_list():
    raw = """
    - a: 1
    - b:
        c: 2
    """

    config_parser = YamlParser()
    config: Config = config_parser.parse(raw)

    assert config == [{"a": 1}, {"b": {"c": 2}}]


def test_yaml_config_parser_invalid_yaml():
    raw = """
    a: 1
      b: 2
    """

    config_parser = YamlParser()

    with pytest.raises(ConfigError):
        config_parser.parse(raw)


# -----------------
# JSON Config_parser
# -----------------


def test_json_config_parser_object():
    raw = '{"a": 1, "b": {"c": 2}}'

    config_parser = JsonParser()
    config = config_parser.parse(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_json_config_parser_list():
    raw = "[1, 2, 3]"

    config_parser = JsonParser()

    config = config_parser.parse(raw)
    assert config == [1, 2, 3]


def test_json_config_parser_invalid_json():
    raw = '{"a": 1,}'

    config_parser = JsonParser()

    with pytest.raises(ConfigError):
        config_parser.parse(raw)


# -----------------
# TOML Config_parser
# -----------------


def test_toml_config_parser_object():
    raw = """
    a = 1

    [b]
    c = 2
    """

    config_parser = TomlParser()
    config = config_parser.parse(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_toml_config_parser_invalid_toml():
    raw = """
    a = 1
    b =
    """

    config_parser = TomlParser()

    with pytest.raises(ConfigError):
        config_parser.parse(raw)


def test_toml_config_parser_missing_dependency(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name in {"tomllib", "tomli"}:
            raise ModuleNotFoundError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    config_parser = TomlParser()

    with pytest.raises(ConfigError):
        config_parser.parse("a = 1")


# -----------------
# XML Config_parser
# -----------------


def test_xml_config_parser_mapping():
    raw = """
    <root>
        <a>1</a>
        <b>
            <c>2</c>
        </b>
    </root>
    """

    config_parser = XmlParser()
    config: Config = config_parser.parse(raw)

    assert config == {"root": {"a": "1", "b": {"c": "2"}}}


def test_xml_config_parser_list():
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

    config_parser = XmlParser()
    config: Config = config_parser.parse(raw)

    assert config == {
        "root": {
            "item": [
                {"a": "1"},
                {"b": "2"},
            ]
        }
    }


def test_xml_config_parser_invalid_xml():
    raw = """
    <root>
        <a>1</b>
    </root>
    """

    config_parser = XmlParser()

    with pytest.raises(ConfigError):
        config_parser.parse(raw)
