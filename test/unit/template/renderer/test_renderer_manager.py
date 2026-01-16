import pytest
from unittest.mock import create_autospec

from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_manager import (
    RendererFactory,
    RendererManager,
)

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def settings():
    # instance=True avoids abstract / missing attributes issues
    return create_autospec(RendererSettings, instance=True)

@pytest.fixture
def renderer():
    return create_autospec(Renderer, instance=True)

# ------------------------------------------------------------------
# RendererFactory tests
# ------------------------------------------------------------------

def test_factory_creates_renderer(settings):
    factory = RendererFactory()

    renderer = factory.create(settings)

    assert isinstance(renderer, Renderer)
    assert renderer._settings is settings


# ------------------------------------------------------------------
# RendererManager tests
# ------------------------------------------------------------------

def test_get_or_create_creates_new_renderer(settings):
    manager = RendererManager()

    renderer = manager.get_or_create(settings)

    assert isinstance(renderer, Renderer)
    assert renderer._settings is settings
    assert settings in manager


def test_get_or_create_returns_cached_instance(settings):
    manager = RendererManager()

    r1 = manager.get_or_create(settings)
    r2 = manager.get_or_create(settings)

    assert r1 is r2


def test_contains_returns_false_when_not_present(settings):
    manager = RendererManager()

    assert settings not in manager


def test_contains_returns_true_when_present(settings):
    manager = RendererManager()
    manager.get_or_create(settings)

    assert settings in manager


def test_preseeded_renderers_are_used(settings, renderer):
    manager = RendererManager(
        renderers={settings: renderer}
    )

    result = manager.get_or_create(settings)

    assert result is renderer
