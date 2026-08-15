import pytest

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.settings import Settings
from templisafe.settings.template_engine_settings import (
    TemplateEngineKind,
    TemplateEngineSettings,
)

# -------------------------
# Sample configurations
# -------------------------

DICT_CONFIG = {"engine_kind": "jinja", "config": {"option1": True, "option2": 42}}

YAML_CONFIG = """
engine_kind: django
config:
  optionA: hello
  optionB: 123
"""

JSON_CONFIG = '{"engine_kind": "jinja", "config": {"x": 1, "y": 2}}'

CUSTOM_DICT_CONFIG = {
    "engine_kind": "custom",
    "config": {"option1": True, "option2": 42},
}

# -------------------------
# Tests
# -------------------------


def test_create_default():
    settings = TemplateEngineSettings.create()
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {}


def test_create_from_dict():
    settings = TemplateEngineSettings.from_dict(DICT_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {"option1": True, "option2": 42}


def test_create_custom_from_dict():
    settings = TemplateEngineSettings.from_dict(CUSTOM_DICT_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.CUSTOM
    assert settings.config == {"option1": True, "option2": 42}


def test_create_from_yaml():
    settings = TemplateEngineSettings.from_yaml(YAML_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.DJANGO
    assert settings.config == {"optionA": "hello", "optionB": 123}


def test_create_from_json():
    settings = TemplateEngineSettings.from_json(JSON_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {"x": 1, "y": 2}


def test_create_invalid_kind():
    config = {"kind": "invalid", "config": {}}
    with pytest.raises(ValueError):
        TemplateEngineSettings.from_dict(config)


def test_create_multiple_config_sources():
    config = {
        "engine_kind": "jinja",
        "config": {},
        "config_yaml": "engine_kind: jinja\nconfig:\n  a: 1",
    }
    with pytest.raises(ValueError, match="Multiple configuration sources"):
        TemplateEngineSettings.from_dict(config)


def test_create_invalid_config_type():
    config = {"engine_kind": "jinja", "config": "not a dict"}
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


def test_create_kwargs_from_base_settings():
    config: dict = {
        "kind": "template_engine_settings",
        "engine_kind": "jinja",
        "config": {"option1": True, "option2": 42},
    }
    settings = Settings.create(**config)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {"option1": True, "option2": 42}


def test_create_kwargs_standard_engine():
    settings = TemplateEngineSettings.create(**DICT_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {"option1": True, "option2": 42}


def test_create_kwargs_custom_engine():
    settings = TemplateEngineSettings.create(**CUSTOM_DICT_CONFIG)
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.CUSTOM
    assert settings.config == {"option1": True, "option2": 42}


def test_create_kwargs_no_config():
    settings = TemplateEngineSettings.create(engine_kind="jinja")
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {}


def test_create_kwargs_invalid_kind():
    with pytest.raises(ValueError):
        TemplateEngineSettings.create(engine_kind="invalid", config={})


def test_create_kwargs_with_yaml_config():
    settings = TemplateEngineSettings.create(engine_kind="django", config_yaml="optionA: hello\noptionB: 123")
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.DJANGO
    assert settings.config == {"optionA": "hello", "optionB": 123}


def test_create_kwargs_with_json_config():
    settings = TemplateEngineSettings.create(engine_kind="jinja", config_json='{"x": 1, "y": 2}')
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA
    assert settings.config == {"x": 1, "y": 2}


def test_create_kwargs_multiple_config_sources_error():
    cfg = {"engine_kind": "jinja", "config": {}, "config_yaml": YAML_CONFIG}
    with pytest.raises(ValueError, match="Multiple configuration sources"):
        TemplateEngineSettings.create(**cfg)

    cfg = {"engine_kind": "jinja", "config": {}, "config_json": JSON_CONFIG}
    with pytest.raises(ValueError, match="Multiple configuration sources"):
        TemplateEngineSettings.create(**cfg)

    cfg = {
        "engine_kind": "jinja",
        "config_yaml": YAML_CONFIG,
        "config_json": JSON_CONFIG,
    }
    with pytest.raises(ValueError, match="Multiple configuration sources"):
        TemplateEngineSettings.create(**cfg)
