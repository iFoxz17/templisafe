import pytest
from typing import Any, Set, Dict

from templisafe.settings.template_engine_settings import (
    TemplateEngineKind,
    CustomTemplateEngineSettings
)
from templisafe.engine.custom_template_engine import CustomTemplateEngine

# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def custom_settings() -> CustomTemplateEngineSettings:
    """Custom settings for testing the CustomTemplateEngine."""
    
    def extract_vars(template: str, config: dict[str, Any]) -> Set[str]:
        # Trivial extraction: find '{{a}}' as a variable
        return {"a"} if "{{a}}" in template else set()
    
    def render(template: str, values: Dict[str, Any], config: dict[str, Any]) -> str:
        # Trivial render: replace '{{a}}' with values['a'] or '1'
        return template.replace("{{a}}", str(values.get("a", 1)))

    return CustomTemplateEngineSettings(
        kind=TemplateEngineKind.CUSTOM,
        config={},
        extract_variables_func=extract_vars,
        render_func=render
    )


@pytest.fixture
def custom_engine(custom_settings) -> CustomTemplateEngine:
    """Return a CustomTemplateEngine instance for testing."""
    return CustomTemplateEngine(custom_settings)


# -------------------------
# CustomTemplateEngine tests
# -------------------------
def test_custom_engine_extract(custom_engine: CustomTemplateEngine):
    template = "Value is {{a}}"
    vars_ = custom_engine.extract_variables(template)
    assert vars_ == {"a"}

    template_no_vars = "Hello world!"
    vars_ = custom_engine.extract_variables(template_no_vars)
    assert vars_ == set()


def test_custom_engine_render(custom_engine: CustomTemplateEngine):
    template = "Value is {{a}}"
    rendered = custom_engine.render(template, {"a": 42})
    assert rendered == "Value is 42"

    # Default value if 'a' not provided
    rendered = custom_engine.render(template, {})
    assert rendered == "Value is 1"