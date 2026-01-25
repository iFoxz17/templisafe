import pytest

from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.template_engine_settings import (
    TemplateEngineSettings,
    TemplateEngineKind,
)
from templisafe.engine.template_engine_manager import (
    TemplateEngineFactory,
    TemplateEngineManager,
)
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.engine.django_template_engine import DjangoTemplateEngine
from templisafe.exceptions.template_engine_error import UnsupportedTemplateEngineError


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def factory() -> TemplateEngineFactory:
    return TemplateEngineFactory()


# Caching is not supported at the moment
#@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
@pytest.fixture(params=[False], ids=["cache_disabled"])
def manager(request) -> TemplateEngineManager:
    """TemplateEngineManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return TemplateEngineManager(settings=settings)


@pytest.fixture
def jinja_settings() -> TemplateEngineSettings:
    return TemplateEngineSettings(
        engine_kind=TemplateEngineKind.JINJA,
        config={}
    )


@pytest.fixture
def django_settings() -> TemplateEngineSettings:
    return TemplateEngineSettings(
        engine_kind=TemplateEngineKind.DJANGO,
        config={}
    )


# -----------------------------
# TemplateEngineFactory tests
# -----------------------------

@pytest.mark.parametrize(
    "settings_fixture, expected_class",
    [
        ("jinja_settings", JinjaTemplateEngine),
        ("django_settings", DjangoTemplateEngine),
    ]
)
def test_factory_creates_engines(
    factory: TemplateEngineFactory,
    settings_fixture: str,
    expected_class: type,
    request,
):
    """TemplateEngineFactory returns correct engine for given settings."""
    settings = request.getfixturevalue(settings_fixture)
    engine = factory.create(settings)
    assert isinstance(engine, expected_class)


def test_factory_custom_engine():
    settings = TemplateEngineSettings(
        engine_kind=TemplateEngineKind.CUSTOM,
        config={}
    )

    with pytest.raises(UnsupportedTemplateEngineError):
        TemplateEngineFactory().create(settings)

# -----------------------------
# TemplateEngineManager tests
# -----------------------------

@pytest.mark.parametrize(
    "settings_fixture, expected_class",
    [
        ("jinja_settings", JinjaTemplateEngine),
        ("django_settings", DjangoTemplateEngine),
    ]
)
def test_manager_caching_behavior(
    manager: TemplateEngineManager,
    settings_fixture: str,
    expected_class: type,
    request,
):
    settings = request.getfixturevalue(settings_fixture)

    engine1 = manager.get_or_create(settings)
    engine2 = manager.get_or_create(settings)

    assert isinstance(engine1, expected_class)
    assert isinstance(engine2, expected_class)

    if manager._settings.cache:
        assert engine1 is engine2
        assert settings in manager
    else:
        assert engine1 is not engine2
        assert settings not in manager


def test_manager_contains_only_cached_engines(
    manager: TemplateEngineManager,
    jinja_settings: TemplateEngineSettings,
):
    """__contains__ reflects cached engines only."""
    assert jinja_settings not in manager

    engine = manager.get_or_create(jinja_settings)

    if manager._settings.cache:
        assert jinja_settings in manager
    else:
        assert jinja_settings not in manager
