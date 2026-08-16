import pytest

from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.settings.template_engine_settings import (
    TemplateEngineKind,
    TemplateEngineSettings,
)


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def basic_settings() -> TemplateEngineSettings:
    """Provide basic Jinja engine settings with default config."""
    return TemplateEngineSettings(engine_kind=TemplateEngineKind.JINJA, config={})


@pytest.fixture
def engine(basic_settings) -> JinjaTemplateEngine:
    """Create a JinjaTemplateEngine instance."""
    return JinjaTemplateEngine(basic_settings)


# -------------------------
# Tests
# -------------------------
def test_initialization(engine: JinjaTemplateEngine):
    """Test that the engine initializes correctly and has _env and _meta attributes."""
    assert hasattr(engine, "_env")
    assert hasattr(engine, "_meta")


def test_extract_variables_simple(engine: JinjaTemplateEngine):
    """Test variable extraction from a simple template."""
    template = "Hello {{ name }}!"
    vars_ = engine.extract_variables(template)
    assert vars_ == {"name"}


def test_extract_variables_multiple(engine: JinjaTemplateEngine):
    """Test variable extraction with multiple and repeated variables."""
    template = "{{ user }} has {{ count }} messages. {{ user }} is online."
    vars_ = engine.extract_variables(template)
    assert vars_ == {"user", "count"}


def test_extract_variables_no_vars(engine: JinjaTemplateEngine):
    """Test template with no variables."""
    template = "Hello World!"
    vars_ = engine.extract_variables(template)
    assert vars_ == set()


def test_render_simple(engine: JinjaTemplateEngine):
    """Test rendering a template with one variable."""
    template = "Hello {{ name }}!"
    result = engine.render(template, {"name": "Alice"})
    assert result == "Hello Alice!"


def test_render_multiple(engine: JinjaTemplateEngine):
    """Test rendering a template with multiple variables."""
    template = "{{ user }} has {{ count }} messages."
    result = engine.render(template, {"user": "Bob", "count": 5})
    assert result == "Bob has 5 messages."


def test_render_uses_loader_from_settings(tmp_path):
    """Test rendering a template that imports a macro through the configured Jinja loader."""
    from jinja2 import FileSystemLoader

    macro_file = tmp_path / "greetings.j2"
    macro_file.write_text("{% macro hello(name) %}Hello {{ name }}!{% endmacro %}", encoding="utf-8")
    settings = TemplateEngineSettings.create(
        engine_kind="jinja",
        config={"loader": FileSystemLoader(str(tmp_path))},
    )
    engine = JinjaTemplateEngine(settings)

    assert engine.extract_variables('{% import "greetings.j2" as greetings %}{{ greetings.hello(name) }}') == {"name"}
    assert engine.render('{% import "greetings.j2" as greetings %}{{ greetings.hello(name) }}', {"name": "Alice"}) == (
        "Hello Alice!"
    )


def test_lazy_import_error(monkeypatch):
    """Test that ImportError is raised if Jinja2 is missing."""
    import builtins

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("jinja2"):
            raise ImportError
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    from templisafe.settings.template_engine_settings import (
        TemplateEngineKind,
        TemplateEngineSettings,
    )

    settings = TemplateEngineSettings(engine_kind=TemplateEngineKind.JINJA, config={})

    with pytest.raises(ImportError, match="Jinja2 is not installed"):
        JinjaTemplateEngine(settings)
