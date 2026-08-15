import pytest

from templisafe.parser.schema.schema_parser_assembler import (
    DEFAULT_MANAGER_SETTINGS,
    SchemaParserAssembler,
)
from templisafe.parser.schema.schema_parser_manager import SchemaParserManager
from templisafe.parser.schema.schema_parser_resolver import SchemaParserResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""

# -----------------------------
# Default settings
# -----------------------------
DEFAULT_SCHEMA_PARSER_SETTINGS: SchemaParserSettings = SchemaParserSettings.create()


# -----------------------------
# Tests
# -----------------------------
def test_assemble_with_defaults():
    assembler = SchemaParserAssembler()
    resolver: SchemaParserResolver = assembler.assemble()

    assert isinstance(resolver, SchemaParserResolver)
    assert isinstance(resolver._schema_parser_manager, SchemaParserManager)
    assert resolver._schema_parser_manager._settings == DEFAULT_MANAGER_SETTINGS
    assert resolver._default_settings == DEFAULT_SCHEMA_PARSER_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = SchemaParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, SchemaParserResolver)
    assert resolver._schema_parser_manager._settings == manager_settings


def test_assemble_with_custom_schema_parser_settings():
    assembler = SchemaParserAssembler()
    custom_settings = SchemaParserSettings.create(allowed_types=("int", "str"), type_aliases={"integer": "int"})
    resolver = assembler.assemble(default_schema_parser_settings=custom_settings)

    assert resolver._default_settings == custom_settings


def test_assemble_with_all_custom_settings():
    assembler = SchemaParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    custom_schema_parser_settings = SchemaParserSettings.create(
        allowed_types=("int", "str"), type_aliases={"integer": "int"}
    )

    resolver = assembler.assemble(
        manager_settings=manager_settings,
        default_schema_parser_settings=custom_schema_parser_settings,
    )

    assert isinstance(resolver, SchemaParserResolver)
    assert resolver._schema_parser_manager._settings == manager_settings
    assert resolver._default_settings == custom_schema_parser_settings
