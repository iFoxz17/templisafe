import pytest

from templisafe.settings.template_engine_settings import (
    TemplateEngineSettings,
    CustomTemplateEngineSettings,
    TemplateEngineKind,
)
from templisafe.exceptions.settings_error import SettingsError


# -------------------------
# Sample configurations
# -------------------------

DICT_CONFIG = {
    "kind": "jinja",
    "config": {"option1": True, "option2": 42}
}

YAML_CONFIG = """
kind: django
config:
  optionA: hello
  optionB: 123
"""

JSON_CONFIG = '{"kind": "jinja", "config": {"x": 1, "y": 2}}'

CUSTOM_CONFIG = {
    "kind": "custom",
    "config": {"custom_option": True},
    "extract_variables_func": lambda tpl, cfg: {"var1", "var2"},
    "render_func": lambda tpl, vars, cfg: tpl.format(**vars)
}


# -------------------------
# Tests
# -------------------------

def test_create_from_dict():
    settings = TemplateEngineSettings.from_dict(DICT_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.JINJA
    assert settings.config == {"option1": True, "option2": 42}


def test_create_from_yaml():
    settings = TemplateEngineSettings.from_yaml(YAML_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.DJANGO
    assert settings.config == {"optionA": "hello", "optionB": 123}


def test_create_from_json():
    settings = TemplateEngineSettings.from_json(JSON_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.JINJA
    assert settings.config == {"x": 1, "y": 2}


def test_create_custom_engine():
    settings = TemplateEngineSettings.from_dict(CUSTOM_CONFIG)
    assert isinstance(settings, CustomTemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.CUSTOM
    assert callable(settings.extract_variables_func)
    assert callable(settings.render_func)
    assert settings.config == {"custom_option": True}


def test_create_invalid_kind():
    config = {"kind": "invalid", "config": {}}
    with pytest.raises(ValueError, match="Invalid template engine kind"):
        TemplateEngineSettings.from_dict(config)


def test_create_missing_kind():
    config = {"config": {}}
    with pytest.raises(ValueError, match="Missing 'kind'"):
        TemplateEngineSettings.from_dict(config)


def test_create_multiple_config_sources():
    config = {
        "kind": "jinja",
        "config": {},
        "config_yaml": "kind: jinja\nconfig:\n  a: 1"
    }
    with pytest.raises(ValueError, match="Multiple configuration sources"):
        TemplateEngineSettings.from_dict(config)


def test_create_invalid_config_type():
    config = {"kind": "jinja", "config": "not a dict"}
    with pytest.raises(ValueError, match="Expected 'config' to be a dict"):
        TemplateEngineSettings.from_dict(config)


def test_from_yaml_non_dict():
    yaml_str = "- item1\n- item2"
    with pytest.raises(SettingsError):
        TemplateEngineSettings.from_yaml(yaml_str)


def test_from_json_non_dict():
    json_str = '["a", "b"]'
    with pytest.raises(SettingsError):
        TemplateEngineSettings.from_json(json_str)


# -------------------------
# Tests for create(**kwargs)
# -------------------------

def test_create_kwargs_standard_engine():
    settings = TemplateEngineSettings.create(**DICT_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert not isinstance(settings, CustomTemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.JINJA
    assert settings.config == {"option1": True, "option2": 42}


def test_create_kwargs_custom_engine():
    settings = TemplateEngineSettings.create(**CUSTOM_CONFIG)
    assert isinstance(settings, CustomTemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.CUSTOM
    assert callable(settings.extract_variables_func)
    assert callable(settings.render_func)
    assert settings.config == {"custom_option": True}


def test_create_kwargs_missing_kind():
    with pytest.raises(ValueError, match="Missing 'kind'"):
        TemplateEngineSettings.create(config={})


def test_create_kwargs_invalid_kind():
    with pytest.raises(ValueError, match="Invalid template engine kind"):
        TemplateEngineSettings.create(kind="invalid", config={})


def test_create_kwargs_custom_missing_callables():
    incomplete = {"kind": "custom", "config": {}}
    with pytest.raises(ValueError, match="CustomTemplateEngineSettings requires 'extract_variables_func' and 'render_func'"):
        TemplateEngineSettings.create(**incomplete)


def test_create_kwargs_with_yaml_config():
    settings = TemplateEngineSettings.create(
        kind="django", 
        config_yaml="optionA: hello\noptionB: 123"
        )
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.DJANGO
    assert settings.config == {"optionA": "hello", "optionB": 123}


def test_create_kwargs_with_json_config():
    settings = TemplateEngineSettings.create(
        kind="jinja", 
        config_json='{"x": 1, "y": 2}'
        )
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.JINJA
    assert settings.config == {"x": 1, "y": 2}


def test_create_kwargs_multiple_config_sources_error():
    cfg = {"kind": "jinja", "config": {}, "config_yaml": YAML_CONFIG}
    with pytest.raises(ValueError, match="Multiple configuration sources"):
        TemplateEngineSettings.create(**cfg)
