import pytest

from templisafe.exceptions.config_error import UnsopportedConfigError
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.config.config_loader import *
from templisafe.config.config_loader_manager import ConfigLoaderFactory, ConfigLoaderManager
from templisafe.util.util import ContentType

# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def factory() -> ConfigLoaderFactory:
    return ConfigLoaderFactory()


@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def manager(request) -> ConfigLoaderManager:
    settings = ManagerSettings(cache=request.param)
    return ConfigLoaderManager(settings=settings)


# -----------------------------
# LoaderFactory tests
# -----------------------------

@pytest.mark.parametrize(
    "content_type, expected_class",
    [
        (ContentType.YAML, YamlConfigLoader),
        (ContentType.JSON, JsonConfigLoader),
        (ContentType.TOML, TomlConfigLoader),
        (ContentType.XML, XmlConfigLoader),
    ],
)
def test_factory_creates_loader(
    factory: ConfigLoaderFactory,
    content_type: ContentType,
    expected_class: type,
):
    """LoaderFactory returns the correct Loader implementation."""
    loader = factory.create(content_type)
    assert isinstance(loader, expected_class)


def test_factory_unsupported_content_type(factory: ConfigLoaderFactory):
    """Unsupported content types raise UnsopportedConfigError."""
    with pytest.raises(UnsopportedConfigError):
        factory.create(ContentType.TEXT)


# -----------------------------
# LoaderManager tests
# -----------------------------

@pytest.mark.parametrize(
    "content_type, expected_class",
    [
        (ContentType.YAML, YamlConfigLoader),
        (ContentType.JSON, JsonConfigLoader),
        (ContentType.TOML, TomlConfigLoader),
        (ContentType.XML, XmlConfigLoader),
    ],
)
def test_manager_get_or_create(
    manager: ConfigLoaderManager,
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


def test_manager_contains_only_cached_loaders(manager: ConfigLoaderManager):
    """__contains__ reflects cached loaders only."""
    assert ContentType.YAML not in manager

    _ = manager.get_or_create(ContentType.YAML)

    if manager._settings.cache:
        assert ContentType.YAML in manager
    else:
        assert ContentType.YAML not in manager
