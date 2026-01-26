import pytest

from templisafe.template.compiler.compiler_assembler import (
    CompilerAssembler,
    DEFAULT_MANAGER_SETTINGS
)
from templisafe.template.compiler.compiler_resolver import CompilerResolver
from templisafe.template.compiler.compiler_manager import CompilerManager
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.compiler_settings import CompilerSettings

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""

CUSTOM_COMPILER_SETTINGS_YAML = """
index_key: custom_index
"""


DEFAULT_COMPILER_SETTINGS: CompilerSettings = CompilerSettings.create()


# -----------------------------
# Tests
# -----------------------------

def test_assemble_with_defaults():
    assembler = CompilerAssembler()
    resolver: CompilerResolver = assembler.assemble()

    assert isinstance(resolver, CompilerResolver)
    assert isinstance(resolver._compiler_manager, CompilerManager)
    assert resolver._compiler_manager._settings == DEFAULT_MANAGER_SETTINGS
    assert resolver._default_settings == DEFAULT_COMPILER_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = CompilerAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, CompilerResolver)
    assert resolver._compiler_manager._settings == manager_settings


def test_assemble_with_custom_compiler_settings():
    assembler = CompilerAssembler()
    custom_settings = CompilerSettings.from_yaml(CUSTOM_COMPILER_SETTINGS_YAML)
    resolver = assembler.assemble(default_compiler_settings=custom_settings)

    assert resolver._default_settings == custom_settings


def test_assemble_with_all_custom_settings():
    assembler = CompilerAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    custom_compiler_settings = CompilerSettings.from_yaml(CUSTOM_COMPILER_SETTINGS_YAML)

    resolver = assembler.assemble(
        manager_settings=manager_settings,
        default_compiler_settings=custom_compiler_settings,
    )

    assert isinstance(resolver, CompilerResolver)
    assert resolver._compiler_manager._settings == manager_settings
    assert resolver._default_settings == custom_compiler_settings
