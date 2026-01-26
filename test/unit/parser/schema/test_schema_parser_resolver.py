from typing import Any
import pytest

from templisafe.parser.schema.schema_loader import SCHEMA_PARSER_SETTINGS_YAML
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.schema.schema_parser_manager import SchemaParserManager
from templisafe.parser.schema.schema_parser_resolver import SchemaParserResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.util import DEFAULT_MANAGER_SETTINGS

# ----------------------------- 
# Fixtures
# ----------------------------- 

SCHEMA_PARSER_SETTINGS_DICT: dict[str, Any] = {
    "schema_key": "schema",
    "type_key": "type",
    "default_key": "default",
    "constraints_key": "constraints",
    "metadata_key": "metadata",
    "index_key": "index",
    "model_name": "MyModel",
    "allowed_types": ["int", "str"],
    "type_aliases": {
        "number": ["int", "float"],
        "text": "str",
    },
}

@pytest.fixture
def default_settings() -> SchemaParserSettings:
    """Return default SchemaParserSettings."""
    return SchemaParserSettings(**SCHEMA_PARSER_SETTINGS_DICT)


@pytest.fixture
def custom_settings() -> SchemaParserSettings:
    """Return custom SchemaParserSettings."""
    return SchemaParserSettings(**SCHEMA_PARSER_SETTINGS_DICT)


@pytest.fixture
def schema_parser_manager() -> SchemaParserManager:
    """Return a SchemaParserManager instance."""
    return SchemaParserManager(
        settings=DEFAULT_MANAGER_SETTINGS
    )


@pytest.fixture
def resolver(
    default_settings: SchemaParserSettings,
    schema_parser_manager: SchemaParserManager
) -> SchemaParserResolver:
    """Return a SchemaParserResolver instance."""
    return SchemaParserResolver(default_settings, schema_parser_manager)


# ----------------------------- 
# SchemaParserResolver tests
# ----------------------------- 

def test_resolver_resolve_with_schema_parser(resolver: SchemaParserResolver):
    """SchemaParserResolver returns the same SchemaParser when passed a SchemaParser instance."""
    schema_parser = SchemaParser(SchemaParserSettings(**SCHEMA_PARSER_SETTINGS_DICT))
    result = resolver.resolve(schema_parser)
    
    assert result is schema_parser
    assert isinstance(result, SchemaParser)


def test_resolver_resolve_with_settings(
    resolver: SchemaParserResolver,
    custom_settings: SchemaParserSettings
):
    """SchemaParserResolver returns a SchemaParser when passed SchemaParserSettings."""
    result = resolver.resolve(custom_settings)
    
    assert isinstance(result, SchemaParser)
    assert result._settings == custom_settings


def test_resolver_resolve_with_none(
    resolver: SchemaParserResolver,
    default_settings: SchemaParserSettings
):
    """SchemaParserResolver returns a SchemaParser with default settings when passed None."""
    result = resolver.resolve(None)
    
    assert isinstance(result, SchemaParser)
    assert result._settings == default_settings


def test_resolver_respects_manager_caching(
    resolver: SchemaParserResolver,
    custom_settings: SchemaParserSettings
):
    """SchemaParserResolver respects SchemaParserManager caching behavior."""
    result1 = resolver.resolve(custom_settings)
    result2 = resolver.resolve(custom_settings)
    
    assert isinstance(result1, SchemaParser)
    assert isinstance(result2, SchemaParser)
    # Assumes manager caching is enabled - adjust based on actual manager behavior
    assert result1 is result2