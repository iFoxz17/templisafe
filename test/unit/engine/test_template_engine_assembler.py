import pytest

from templisafe.engine.template_engine_assembler import (
    TemplateEngineAssembler, 
    DEFAULT_TEMPLATE_ENGINE_SETTINGS_YAML,
    DEFAULT_MANAGER_SETTINGS_YAML
)
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings


CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""
CUSTOM_TEMPLATE_ENGINE_SETTINGS_YAML = """
kind: jinja
config:
  autoescape: true
"""

DEFAULT_MANAGER_SETTINGS: ManagerSettings = ManagerSettings.from_yaml(DEFAULT_MANAGER_SETTINGS_YAML)
DEFAULT_TEMPLATE_ENGINE_SETTINGS: TemplateEngineSettings = (
    TemplateEngineSettings.from_yaml(DEFAULT_TEMPLATE_ENGINE_SETTINGS_YAML)
)


def test_assemble_with_defaults():
    assembler = TemplateEngineAssembler()

    resolver: TemplateEngineResolver = assembler.assemble()

    assert isinstance(resolver, TemplateEngineResolver)
    assert resolver._template_engine_manager._settings == DEFAULT_MANAGER_SETTINGS
    assert resolver._default_settings == DEFAULT_TEMPLATE_ENGINE_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = TemplateEngineAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, TemplateEngineResolver)
    assert resolver._template_engine_manager._settings == manager_settings


def test_assemble_with_custom_template_engine_settings():
    assembler = TemplateEngineAssembler()
    custom_settings = TemplateEngineSettings.from_yaml(
        CUSTOM_TEMPLATE_ENGINE_SETTINGS_YAML
    )
    resolver = assembler.assemble(
        default_template_engine_settings=custom_settings
    )

    assert resolver._default_settings == custom_settings
    

def test_assemble_with_all_custom_settings():
    assembler = TemplateEngineAssembler()

    manager_settings = ManagerSettings.from_yaml(DEFAULT_MANAGER_SETTINGS_YAML)
    custom_template_engine_settings = TemplateEngineSettings.from_yaml(
        CUSTOM_TEMPLATE_ENGINE_SETTINGS_YAML
    )

    resolver = assembler.assemble(
        manager_settings=manager_settings,
        default_template_engine_settings=custom_template_engine_settings,
    )

    assert isinstance(resolver, TemplateEngineResolver)
    assert resolver._template_engine_manager._settings == manager_settings
    assert resolver._default_settings == custom_template_engine_settings
