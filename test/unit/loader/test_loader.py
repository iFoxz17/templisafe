import pytest

from templisafe.exceptions.load_error import LoadError
from templisafe.loader.loader import (
    Loader,
    YamlLoader,
    JsonLoader,
    TomlLoader,
)


def test_loader_is_abstract():
    with pytest.raises(TypeError):
        Loader()        # type: ignore


# -----------------
# YAML Loader
# -----------------

def test_yaml_loader_valid():
    raw = """
    a: 1
    b:
      c: 2
    """

    loader = YamlLoader()
    config = loader.load(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_yaml_loader_invalid_yaml():
    raw = """
    a: 1
      b: 2
    """

    loader = YamlLoader()

    with pytest.raises(LoadError, match="Failed to load YAML configuration"):
        loader.load(raw)


def test_yaml_loader_non_dict():
    raw = """
    - a
    - b
    - c
    """

    loader = YamlLoader()

    with pytest.raises(LoadError, match="YAML configuration must be a mapping"):
        loader.load(raw)


# -----------------
# JSON Loader
# -----------------

def test_json_loader_valid():
    raw = '{"a": 1, "b": {"c": 2}}'

    loader = JsonLoader()
    config = loader.load(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_json_loader_invalid_json():
    raw = '{"a": 1,}'

    loader = JsonLoader()

    with pytest.raises(LoadError, match="Failed to load JSON configuration"):
        loader.load(raw)


def test_json_loader_non_dict():
    raw = '[1, 2, 3]'

    loader = JsonLoader()

    with pytest.raises(LoadError, match="JSON configuration must be an object"):
        loader.load(raw)


# -----------------
# TOML Loader
# -----------------

def test_toml_loader_valid():
    raw = """
    a = 1

    [b]
    c = 2
    """

    loader = TomlLoader()
    config = loader.load(raw)

    assert config == {"a": 1, "b": {"c": 2}}


def test_toml_loader_invalid_toml():
    raw = """
    a = 1
    b =
    """

    loader = TomlLoader()

    with pytest.raises(LoadError, match="Failed to load TOML configuration"):
        loader.load(raw)


def test_toml_loader_missing_dependency(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name in {"tomllib", "tomli"}:
            raise ModuleNotFoundError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    loader = TomlLoader()

    with pytest.raises(
        LoadError,
        match="TOML support requires Python >= 3.11 or the 'tomli' package installed",
    ):
        loader.load("a = 1")
