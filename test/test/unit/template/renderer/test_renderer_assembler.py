from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer_assembler import (
    DEFAULT_MANAGER_SETTINGS,
    RendererAssembler,
)
from templisafe.template.renderer.renderer_manager import RendererManager
from templisafe.template.renderer.renderer_resolver import RendererResolver

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""

CUSTOM_RENDERER_SETTINGS_YAML = """
index_key: custom_index
"""


DEFAULT_RENDERER_SETTINGS: RendererSettings = RendererSettings.create()


# -----------------------------
# Tests
# -----------------------------


def test_assemble_with_defaults():
    assembler = RendererAssembler()
    resolver: RendererResolver = assembler.assemble()

    assert isinstance(resolver, RendererResolver)
    assert isinstance(resolver._renderer_manager, RendererManager)
    assert resolver._renderer_manager._settings == DEFAULT_MANAGER_SETTINGS
    assert resolver._default_settings == DEFAULT_RENDERER_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = RendererAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, RendererResolver)
    assert resolver._renderer_manager._settings == manager_settings


def test_assemble_with_custom_renderer_settings():
    assembler = RendererAssembler()
    custom_settings = RendererSettings.from_yaml(CUSTOM_RENDERER_SETTINGS_YAML)
    resolver = assembler.assemble(default_renderer_settings=custom_settings)

    assert resolver._default_settings == custom_settings


def test_assemble_with_all_custom_settings():
    assembler = RendererAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    custom_renderer_settings = RendererSettings.from_yaml(CUSTOM_RENDERER_SETTINGS_YAML)

    resolver = assembler.assemble(
        manager_settings=manager_settings,
        default_renderer_settings=custom_renderer_settings,
    )

    assert isinstance(resolver, RendererResolver)
    assert resolver._renderer_manager._settings == manager_settings
    assert resolver._default_settings == custom_renderer_settings
