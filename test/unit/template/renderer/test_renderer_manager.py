import pytest

from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_manager import RendererFactory, RendererManager


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def factory() -> RendererFactory:
    """Return a RendererFactory instance."""
    return RendererFactory()


@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def manager(request) -> RendererManager:
    """Return a RendererManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return RendererManager(settings=settings)


@pytest.fixture
def renderer_settings() -> RendererSettings:
    """Return a basic RendererSettings object."""
    return RendererSettings(index_key="_index")


# -----------------------------
# RendererFactory tests
# -----------------------------

def test_factory_creates_renderer(factory: RendererFactory, renderer_settings: RendererSettings):
    """RendererFactory returns a Renderer instance for given settings."""
    renderer = factory.create(renderer_settings)
    assert isinstance(renderer, Renderer)
    assert renderer._settings == renderer_settings


# -----------------------------
# RendererManager tests
# -----------------------------

def test_manager_get_or_create(manager: RendererManager, renderer_settings: RendererSettings):
    """RendererManager returns Renderer instances and respects caching."""
    renderer1 = manager.get_or_create(renderer_settings)
    renderer2 = manager.get_or_create(renderer_settings)

    assert isinstance(renderer1, Renderer)
    assert isinstance(renderer2, Renderer)

    if manager._settings.cache:
        # Should be the same instance if caching enabled
        assert renderer1 is renderer2
        assert renderer_settings in manager
    else:
        # Should be different instances if caching disabled
        assert renderer1 is not renderer2
        assert renderer_settings not in manager


def test_manager_contains_only_cached_renderers(manager: RendererManager, renderer_settings: RendererSettings):
    """__contains__ reflects only cached renderers."""
    # Initially nothing cached
    assert renderer_settings not in manager

    renderer = manager.get_or_create(renderer_settings)

    if manager._settings.cache:
        assert renderer_settings in manager
    else:
        assert renderer_settings not in manager
