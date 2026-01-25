from typing import Any
import pytest

from templisafe.exceptions.template_engine_error import UnsupportedTemplateEngineError
from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineManager, TemplateEngineFactory
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.engine.django_template_engine import DjangoTemplateEngine


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def factory() -> TemplateEngineFactory:
    return TemplateEngineFactory()


@pytest.fixture
def manager(factory) -> TemplateEngineManager:
    """TemplateEngineManager without caching."""
    from templisafe.settings.manager_settings import ManagerSettings
    settings = ManagerSettings(cache=False)
    return TemplateEngineManager(settings=settings, factory=factory)


@pytest.fixture
def jinja_settings() -> TemplateEngineSettings:
    return TemplateEngineSettings(engine_kind=TemplateEngineKind.JINJA, config={})


@pytest.fixture
def django_settings() -> TemplateEngineSettings:
    return TemplateEngineSettings(engine_kind=TemplateEngineKind.DJANGO, config={})


@pytest.fixture
def resolver(manager, jinja_settings) -> TemplateEngineResolver:
    """TemplateEngineResolver with a default engine."""
    return TemplateEngineResolver(default_settings=jinja_settings, template_engine_manager=manager)


# -----------------------------
# Tests
# -----------------------------
def test_resolve_already_engine(resolver: TemplateEngineResolver, jinja_settings):
    """If input is already a TemplateEngine, it is returned as-is."""
    engine1 = resolver._template_engine_manager.get_or_create(jinja_settings)
    engine2 = resolver.resolve(engine1)
    assert engine1 is engine2


def test_resolve_from_settings(resolver: TemplateEngineResolver, django_settings):
    """If input is TemplateEngineSettings, a new TemplateEngine is created."""
    engine = resolver.resolve(django_settings)
    assert isinstance(engine, DjangoTemplateEngine)


def test_resolve_default_settings(resolver: TemplateEngineResolver, jinja_settings):
    """If input is None, resolver returns an engine using default settings."""
    engine = resolver.resolve()
    assert isinstance(engine, JinjaTemplateEngine)
    assert engine._settings == jinja_settings


def test_resolve_multiple_engines(resolver: TemplateEngineResolver, jinja_settings, django_settings):
    """Resolver can create engines for different settings independently."""
    jinja_engine = resolver.resolve(jinja_settings)
    django_engine = resolver.resolve(django_settings)
    assert isinstance(jinja_engine, JinjaTemplateEngine)
    assert isinstance(django_engine, DjangoTemplateEngine)
    assert jinja_engine is not django_engine


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

@pytest.fixture
def custom_engine() -> TemplateEngine:
    """Return an instance of the custom engine."""
    settings = TemplateEngineSettings.create(engine_kind="custom", config={})
    return MyCustomEngine(settings)

def test_resolve_custom_engine(resolver: TemplateEngineResolver, custom_engine):
    """If input is already a TemplateEngine, it is returned as-is."""
    engine = resolver.resolve(custom_engine)
    assert engine is custom_engine

def test_resolve_custom_engine_settings_raises(resolver: TemplateEngineResolver):
    with pytest.raises(UnsupportedTemplateEngineError):
        _ = resolver.resolve(TemplateEngineSettings.create(engine_kind="custom", config={}))


