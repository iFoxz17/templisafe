from typing import Any

import pytest

from templisafe.engine.template_engine import TemplateEngine
from templisafe.settings.template_engine_settings import TemplateEngineSettings


# -------------------------
# Custom TemplateEngine for testing
# -------------------------
class MyCustomEngine(TemplateEngine):
    """A trivial custom template engine for testing purposes."""

    def extract_variables(self, template_str: str) -> set[str]:
        # Trivial extraction: '{{a}}' is the only recognized variable
        return {"a"} if "{{a}}" in template_str else set()

    def render(self, template_str: str, vars_map: dict[str, Any]) -> str:
        # Replace '{{a}}' with the provided value or default to 1
        return template_str.replace("{{a}}", str(vars_map.get("a", 1)))


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def custom_engine() -> TemplateEngine:
    """Return an instance of the custom engine."""
    settings = TemplateEngineSettings.create(engine_kind="custom", config={})
    return MyCustomEngine(settings)


# -------------------------
# Tests
# -------------------------
def test_extract_variables(custom_engine: TemplateEngine):
    template = "Value is {{a}}"
    vars_ = custom_engine.extract_variables(template)
    assert vars_ == {"a"}

    template_no_vars = "Hello world!"
    vars_ = custom_engine.extract_variables(template_no_vars)
    assert vars_ == set()


def test_render(custom_engine: TemplateEngine):
    template = "Value is {{a}}"
    rendered = custom_engine.render(template, {"a": 42})
    assert rendered == "Value is 42"

    # Default value if 'a' not provided
    rendered = custom_engine.render(template, {})
    assert rendered == "Value is 1"
