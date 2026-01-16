from typing import Any

from templisafe.template.template_model import Schema
from templisafe.loader.schema.schema_parser import SchemaParser
from templisafe.loader.schema.schema_parser_manager import SchemaParserManager
from templisafe.settings.schema_parser_settings import SchemaParserSettings

_SCHEMA_KEY_KEY: str = 'schema_key'
_TYPE_KEY_KEY: str = 'type_key'
_DEFAULT_KEY_KEY: str = 'default_key'
_DEFAULT_KEY_KEY: str = 'default_key'
_CONSTRAINTS_KEY_KEY: str = 'constraints_key'
_METADATA_KEY_KEY: str = 'metadata_key'
_INDEX_KEY_KEY: str = 'index_key'
_MODEL_NAME_KEY: str = 'model_name'
_ALLOWED_TYPES_KEY: str = 'allowed_types'
_TYPE_ALIASES_KEY: str = 'type_aliases'

SCHEMA_PARSER_SETTINGS_YAML: str = f"""
{_SCHEMA_KEY_KEY}: schema
{_TYPE_KEY_KEY}: type
{_DEFAULT_KEY_KEY}: default
{_CONSTRAINTS_KEY_KEY}: constraints
{_METADATA_KEY_KEY}: metadata
{_INDEX_KEY_KEY}: _index
{_MODEL_NAME_KEY}: ModelSchema
{_ALLOWED_TYPES_KEY}: [bool, int, float, str, optional, list, dict, date, datetime, object]
{_TYPE_ALIASES_KEY}: 
  bool: [boolean]
  int: [integer]
  float: [real, number]
  str: [string]
  object: [any]
"""

class SchemaLoader:
    """Loads and parses schemas using a configured schema parser."""

    __slots__: tuple[str, ...] = ('_default_settings', '_manager',)

    def __init__(self, default_settings: SchemaParserSettings | None = None) -> None:
        self._default_settings: SchemaParserSettings = default_settings or SchemaParserSettings.from_yaml(SCHEMA_PARSER_SETTINGS_YAML)
        self._manager: SchemaParserManager = SchemaParserManager()

    def _resolve_settings(self, parser_settings: SchemaParserSettings | None = None) -> SchemaParserSettings:
        return parser_settings or self._default_settings

    def load(self, schema_config: dict[str, Any], parser_settings: SchemaParserSettings | None = None) -> Schema:
        """Load and parse a schema from a config using the specified parser settings."""

        parser_settings = self._resolve_settings(parser_settings)
        parser: SchemaParser = self._manager.get_or_create(parser_settings)
        return parser.parse(schema_config)