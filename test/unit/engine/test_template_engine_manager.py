import pytest

from templisafe.settings.template_engine_settings import (
    TemplateEngineSettings, 
    TemplateEngineKind,
)
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.engine.django_template_engine import DjangoTemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineFactory, TemplateEngineManager

# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def jinja_settings() -> TemplateEngineSettings:
    return TemplateEngineSettings(kind=TemplateEngineKind.JINJA, config={})

@pytest.fixture
def django_settings() -> TemplateEngineSettings:
    return TemplateEngineSettings(kind=TemplateEngineKind.DJANGO, config={})

@pytest.fixture
def factory() -> TemplateEngineFactory:
    return TemplateEngineFactory()

@pytest.fixture
def manager() -> TemplateEngineManager:
    return TemplateEngineManager()


# -------------------------
# TemplateEngineFactory tests
# -------------------------
def test_factory_creates_jinja(factory: TemplateEngineFactory, jinja_settings: TemplateEngineSettings):
    engine = factory.create(jinja_settings)
    assert isinstance(engine, JinjaTemplateEngine)

def test_factory_creates_django(factory: TemplateEngineFactory, django_settings: TemplateEngineSettings):
    engine = factory.create(django_settings)
    assert isinstance(engine, DjangoTemplateEngine)

# -------------------------
# TemplateEngineManager tests
# -------------------------
def test_manager_creates_new_instance_each_time(manager: TemplateEngineManager, jinja_settings: TemplateEngineSettings):
    engine1 = manager.get_or_create(jinja_settings)
    engine2 = manager.get_or_create(jinja_settings)
    assert isinstance(engine1, JinjaTemplateEngine)
    assert isinstance(engine2, JinjaTemplateEngine)
    # Should be different instances (no caching)
    assert engine1 is not engine2

def test_manager_creates_django_instance(manager: TemplateEngineManager, django_settings: TemplateEngineSettings):
    engine = manager.get_or_create(django_settings)
    assert isinstance(engine, DjangoTemplateEngine)
