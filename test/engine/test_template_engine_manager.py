import pytest

from templisafe.settings.template_engine_settings import (
    TemplateEngineSettings, 
    TemplateEngineKind, 
    CustomTemplateEngineSettings
)
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.engine.django_template_engine import DjangoTemplateEngine
from templisafe.engine.custom_template_engine import CustomTemplateEngine
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
def custom_settings() -> CustomTemplateEngineSettings:
    return CustomTemplateEngineSettings(
        kind=TemplateEngineKind.CUSTOM, 
        config={},
        extract_variables_func=lambda x, config: {"a"},
        render_func=lambda template_str, values, config: template_str.replace("{{a}}", str(values.get("a", 1)))
    )

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

def test_factory_creates_custom(factory: TemplateEngineFactory, custom_settings: CustomTemplateEngineSettings):
    engine = factory.create(custom_settings)
    assert isinstance(engine, CustomTemplateEngine)
    # Also test the callable functions work
    assert engine.extract_variables("{{a}}") == {"a"}
    assert engine.render("Value {{a}}", {"a": 42}) == "Value 42"

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

def test_manager_creates_custom_instance(manager: TemplateEngineManager, custom_settings: CustomTemplateEngineSettings):
    engine = manager.get_or_create(custom_settings)
    assert isinstance(engine, CustomTemplateEngine)
    # Check extract/render functions
    assert engine.extract_variables("{{a}}") == {"a"}
    assert engine.render("Value {{a}}", {"a": 99}) == "Value 99"

def test_manager_mixed_engines(manager: TemplateEngineManager, jinja_settings: TemplateEngineSettings, custom_settings: CustomTemplateEngineSettings):
    jinja_engine = manager.get_or_create(jinja_settings)
    custom_engine = manager.get_or_create(custom_settings)
    from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
    assert isinstance(jinja_engine, JinjaTemplateEngine)
    assert isinstance(custom_engine, CustomTemplateEngine)
    # Ensure different instances
    assert jinja_engine is not custom_engine
