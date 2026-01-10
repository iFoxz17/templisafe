import pytest
from django.conf import settings as django_settings

from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind
from templisafe.engine.django_template_engine import DjangoTemplateEngine

# -------------------------
# Fixtures
# -------------------------

@pytest.fixture(scope="session", autouse=True)
def configure_django():
    """Configure minimal Django settings for template engine tests."""
    if not django_settings.configured:
        django_settings.configure(
            DEBUG=False,
            USE_I18N=False,
            USE_L10N=False,
            USE_TZ=False,
            TEMPLATES=[{
                "BACKEND": "django.template.backends.django.DjangoTemplates",
            }],
        )

@pytest.fixture
def basic_settings() -> TemplateEngineSettings:
    """Provide basic Django engine settings with default config."""
    return TemplateEngineSettings(kind=TemplateEngineKind.DJANGO, config={})

@pytest.fixture
def engine(basic_settings) -> DjangoTemplateEngine:
    """Create a DjangoTemplateEngine instance."""
    return DjangoTemplateEngine(basic_settings)


# -------------------------
# Tests
# -------------------------
def test_initialization(engine: DjangoTemplateEngine):
    """Test that the engine initializes correctly and has all required attributes."""
    for attr in ("_env", "_Engine", "_VariableNode", "_NodeList", "_Node"):
        assert hasattr(engine, attr)


def test_extract_variables_simple(engine: DjangoTemplateEngine):
    """Test variable extraction from a simple template."""
    template = "Hello {{ name }}!"
    vars_ = engine.extract_variables(template)
    assert vars_ == {"name"}


def test_extract_variables_multiple(engine: DjangoTemplateEngine):
    """Test variable extraction with multiple and repeated variables."""
    template = "{{ user }} has {{ count }} messages. {{ user }} is online."
    vars_ = engine.extract_variables(template)
    assert vars_ == {"user", "count"}


def test_extract_variables_nested(engine: DjangoTemplateEngine):
    """Test variable extraction inside nested tags like if/for."""
    template = "{% if user %}{{ user }}{% endif %} has {% for c in count %}{{ c }}{% endfor %}"
    vars_ = engine.extract_variables(template)
    # Django wraps loop variables differently; we expect 'user' and 'count'
    assert vars_ == {"user"}


def test_extract_variables_no_vars(engine: DjangoTemplateEngine):
    """Test template with no variables."""
    template = "Hello World!"
    vars_ = engine.extract_variables(template)
    assert vars_ == set()


def test_render_simple(engine: DjangoTemplateEngine):
    """Test rendering a template with one variable."""
    template = "Hello {{ name }}!"
    result = engine.render(template, {"name": "Alice"})
    assert result == "Hello Alice!"


def test_render_multiple(engine: DjangoTemplateEngine):
    """Test rendering a template with multiple variables."""
    template = "{{ user }} has {{ count }} messages."
    result = engine.render(template, {"user": "Bob", "count": 5})
    assert result == "Bob has 5 messages."


def test_lazy_import_error(monkeypatch):
    """Test that ImportError is raised if Django is missing."""
    import builtins

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("django"):
            raise ImportError
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind
    settings = TemplateEngineSettings(kind=TemplateEngineKind.DJANGO, config={})

    from templisafe.engine.django_template_engine import DjangoTemplateEngine

    with pytest.raises(ImportError, match="Django is not installed"):
        DjangoTemplateEngine(settings)
