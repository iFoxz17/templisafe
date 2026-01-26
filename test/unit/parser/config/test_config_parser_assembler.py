import pytest
from templisafe.parser.config.config_parser_assembler import ConfigParserAssembler
from templisafe.parser.config.config_parser_resolver import ConfigParserResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.util import DEFAULT_MANAGER_SETTINGS

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""

def test_assemble_with_defaults():
    assembler = ConfigParserAssembler()

    resolver: ConfigParserResolver = assembler.assemble()

    assert isinstance(resolver, ConfigParserResolver)
    assert resolver._config_parser_manager._settings == DEFAULT_MANAGER_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = ConfigParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, ConfigParserResolver)
    assert resolver._config_parser_manager._settings == manager_settings
