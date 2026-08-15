import pytest

from templisafe.content.content import ContentType
from templisafe.exceptions.config_error import UnsupportedConfigError
from templisafe.parser.config.config_parser import *
from templisafe.parser.config.config_parser_manager import (
    ConfigParserFactory,
    ConfigParserManager,
)
from templisafe.settings.manager_settings import ManagerSettings

# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def factory() -> ConfigParserFactory:
    return ConfigParserFactory()


@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def manager(request) -> ConfigParserManager:
    settings = ManagerSettings(cache=request.param)
    return ConfigParserManager(settings=settings)


# -----------------------------
# LoaderFactory tests
# -----------------------------


@pytest.mark.parametrize(
    "content_type, expected_class",
    [
        (ContentType.YAML, YamlParser),
        (ContentType.JSON, JsonParser),
        (ContentType.TOML, TomlParser),
        (ContentType.XML, XmlParser),
    ],
)
def test_factory_creates_loader(
    factory: ConfigParserFactory,
    content_type: ContentType,
    expected_class: type,
):
    """LoaderFactory returns the correct Loader implementation."""
    loader = factory.create(content_type)
    assert isinstance(loader, expected_class)


def test_factory_unsupported_content_type(factory: ConfigParserFactory):
    """Unsupported content types raise UnsupportedConfigError."""
    with pytest.raises(UnsupportedConfigError):
        factory.create(ContentType.TEXT)


# -----------------------------
# LoaderManager tests
# -----------------------------


@pytest.mark.parametrize(
    "content_type, expected_class",
    [
        (ContentType.YAML, YamlParser),
        (ContentType.JSON, JsonParser),
        (ContentType.TOML, TomlParser),
        (ContentType.XML, XmlParser),
    ],
)
def test_manager_get_or_create(
    manager: ConfigParserManager,
    content_type: ContentType,
    expected_class: type,
):
    """Manager returns loaders and respects caching behavior."""
    loader1 = manager.get_or_create(content_type)
    loader2 = manager.get_or_create(content_type)

    assert isinstance(loader1, expected_class)
    assert isinstance(loader2, expected_class)

    if manager._settings.cache:
        assert loader1 is loader2
        assert content_type in manager
    else:
        assert loader1 is not loader2
        assert content_type not in manager


def test_manager_contains_only_cached_loaders(manager: ConfigParserManager):
    """__contains__ reflects cached loaders only."""
    assert ContentType.YAML not in manager

    _ = manager.get_or_create(ContentType.YAML)

    if manager._settings.cache:
        assert ContentType.YAML in manager
    else:
        assert ContentType.YAML not in manager
