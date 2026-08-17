from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.settings.settings_parser_assembler import SettingsParserAssembler
from templisafe.parser.settings.settings_parser_resolver import SettingsParserResolver
from templisafe.settings.manager_settings import ManagerSettings

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""

# -----------------------------
# Tests
# -----------------------------


def test_assemble_with_defaults():
    assembler = SettingsParserAssembler()

    resolver: SettingsParserResolver = assembler.assemble()

    assert isinstance(resolver, SettingsParserResolver)
    assert resolver._settings_parser_manager._settings == DEFAULT_MANAGER_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = SettingsParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, SettingsParserResolver)
    assert resolver._settings_parser_manager._settings == manager_settings
