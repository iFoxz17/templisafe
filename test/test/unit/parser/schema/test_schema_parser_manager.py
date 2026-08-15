import pytest

from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.schema.schema_parser_manager import (
    SchemaParserFactory,
    SchemaParserManager,
)
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings


# -----------------------------
# SchemaParserManager fixture (cache enabled and disabled)
# -----------------------------
@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def schema_parser_manager(request) -> SchemaParserManager:
    """Create a SchemaParserManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return SchemaParserManager(settings=settings)


# -----------------------------
# SchemaParserSettings fixtures
# -----------------------------

SCHEMA_PARSER_SETTINGS_YAML: str = f"""
schema_key: schema
type_key: type
default_key: default
constraints_key: constraints
metadata_key: metadata
index_key: _index
model_name: ModelSchema
allowed_types: [bool, int, float, str, optional, list, dict, date, datetime, object]
type_aliases: 
  bool: [boolean]
  int: [integer]
  float: [real, number]
  str: [string]
  object: [any]
"""


@pytest.fixture
def default_schema_settings() -> SchemaParserSettings:
    return SchemaParserSettings.from_yaml(SCHEMA_PARSER_SETTINGS_YAML)


@pytest.fixture
def custom_schema_settings(
    default_schema_settings: SchemaParserSettings,
) -> SchemaParserSettings:
    return default_schema_settings.model_copy(update={"schema_key": "custom_schema"})


# -----------------------------
# SchemaParserFactory tests
# -----------------------------
@pytest.mark.parametrize("settings_fixture", ["default_schema_settings", "custom_schema_settings"])
def test_factory_creates_schema_parser(settings_fixture, request):
    """SchemaParserFactory returns a SchemaParser instance for the given settings."""
    settings = request.getfixturevalue(settings_fixture)
    parser = SchemaParserFactory().create(settings)

    assert isinstance(parser, SchemaParser)
    assert parser._settings == settings


# -----------------------------
# SchemaParserManager caching behavior
# -----------------------------
def test_manager_caching_behavior(
    default_schema_settings,
    custom_schema_settings,
    schema_parser_manager: SchemaParserManager,
):
    """Test that SchemaParserManager caches parsers only if caching is enabled."""
    manager = schema_parser_manager

    # Default settings
    parser1 = manager.get_or_create(default_schema_settings)
    parser2 = manager.get_or_create(default_schema_settings)

    if manager._settings.cache:
        assert parser1 is parser2
        assert default_schema_settings in manager
    else:
        assert parser1 is not parser2
        assert default_schema_settings not in manager

    # Custom settings
    parser3 = manager.get_or_create(custom_schema_settings)
    parser4 = manager.get_or_create(custom_schema_settings)

    if manager._settings.cache:
        assert parser3 is parser4
        assert custom_schema_settings in manager
    else:
        assert parser3 is not parser4
        assert custom_schema_settings not in manager
