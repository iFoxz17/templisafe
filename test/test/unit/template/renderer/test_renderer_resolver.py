import pytest

from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_manager import (
    RendererFactory,
    RendererManager,
)
from templisafe.template.renderer.renderer_resolver import RendererResolver


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def factory() -> RendererFactory:
    """Return a RendererFactory instance."""
    return RendererFactory()


@pytest.fixture
def manager(factory) -> RendererManager:
    """RendererManager without caching."""
    settings = ManagerSettings(cache=False)
    return RendererManager(settings=settings, factory=factory)


@pytest.fixture
def renderer_settings() -> RendererSettings:
    """Return a basic RendererSettings object."""
    return RendererSettings(index_key="_index")


@pytest.fixture
def resolver(manager, renderer_settings) -> RendererResolver:
    """RendererResolver with default renderer settings."""
    return RendererResolver(default_settings=renderer_settings, renderer_manager=manager)


# -----------------------------
# Tests
# -----------------------------
def test_resolve_already_renderer(resolver: RendererResolver, renderer_settings: RendererSettings):
    """If input is already a Renderer, it is returned as-is."""
    renderer1 = resolver._renderer_manager.get_or_create(renderer_settings)
    renderer2 = resolver.resolve(renderer1)
    assert renderer1 is renderer2


def test_resolve_from_settings(resolver: RendererResolver):
    """If input is RendererSettings, a new Renderer is created."""
    new_settings = RendererSettings(index_key="_key_index")
    renderer = resolver.resolve(new_settings)
    assert isinstance(renderer, Renderer)
    assert renderer._settings == new_settings


def test_resolve_default_settings(resolver: RendererResolver, renderer_settings: RendererSettings):
    """If input is None, resolver returns a Renderer using default settings."""
    renderer = resolver.resolve()
    assert isinstance(renderer, Renderer)
    assert renderer._settings == renderer_settings


def test_resolve_multiple_renderers(resolver: RendererResolver):
    """Resolver can create Renderers for different settings independently."""
    settings1 = RendererSettings(index_key="_key_index_1")
    settings2 = RendererSettings(index_key="_key_index_2")

    renderer1 = resolver.resolve(settings1)
    renderer2 = resolver.resolve(settings2)

    assert isinstance(renderer1, Renderer)
    assert isinstance(renderer2, Renderer)
    assert renderer1 is not renderer2
    assert renderer1._settings != renderer2._settings
