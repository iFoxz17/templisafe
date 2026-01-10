import pytest
from typing import Any, Dict, Set

from templisafe.settings.template_engine_settings import (
    TemplateEngineSettings,
    CustomTemplateEngineSettings,
    TemplateEngineKind
)


# -------------------------
# Test basic creation
# -------------------------
def test_create_jinja_with_dict():
    settings = TemplateEngineSettings.create(kind="jinja", config={"debug": True})
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.JINJA
    assert settings.config == {"debug": True}


def test_create_django_with_enum():
    settings = TemplateEngineSettings.create(kind=TemplateEngineKind.DJANGO, config={"foo": 123})
    assert isinstance(settings, TemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.DJANGO
    assert settings.config["foo"] == 123


# -------------------------
# Test invalid kind
# -------------------------
def test_create_invalid_kind_raises():
    with pytest.raises(ValueError, match="Invalid template engine kind"):
        TemplateEngineSettings.create(kind="unknown", config={})


def test_create_missing_kind_raises():
    with pytest.raises(ValueError, match="Missing 'kind' field"):
        TemplateEngineSettings.create(config={})


# -------------------------
# Test invalid config
# -------------------------
def test_create_invalid_config_type_raises():
    with pytest.raises(ValueError, match="Expected 'config' to be a dict"):
        TemplateEngineSettings.create(kind="jinja", config="not-a-dict")


# -------------------------
# Test CustomTemplateEngineSettings creation
# -------------------------
def test_create_custom_requires_funcs():
    # Missing funcs should raise
    with pytest.raises(ValueError, match="CustomTemplateEngineSettings requires"):
        TemplateEngineSettings.create(kind="custom", config={})

def test_create_custom_with_funcs():
    def extract_vars(template: str) -> Set[str]:
        return {"x"}

    def render(template: str, values: Dict[str, Any]) -> str:
        return template.replace("{{x}}", str(values.get("x", 0)))

    settings = TemplateEngineSettings.create(
        kind="custom",
        config={"foo": 1},
        extract_variables_func=extract_vars,
        render_func=render
    )

    assert isinstance(settings, CustomTemplateEngineSettings)
    assert settings.kind == TemplateEngineKind.CUSTOM
    assert settings.config == {"foo": 1}
    # Callables work
    assert settings.extract_variables_func("{{x}}") == {"x"}
    assert settings.render_func("Value {{x}}", {"x": 42}) == "Value 42"