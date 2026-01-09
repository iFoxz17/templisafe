from overrides import overrides
from typing import Any

from sqltemplater.template.template_model import Schema
from sqltemplater.loader.schema.schema_parser import SchemaParser
from sqltemplater.source.source import Source
from sqltemplater.source.inline_source import InlineSource
from sqltemplater.settings.source_settings import InlineSourceSettings
from sqltemplater.loader.schema.schema_parser_manager import SchemaParserManager
from sqltemplater.loader.loader import Loader, LoaderContext
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings, SchemaParserSettings
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.schema_error import IllegalSchemaDefinitionError, UnsupportedSchemaParserError

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

SCHEMA_PARSER_SETTINGS: str = f"""
default_diagnostic_policy: RAISE_WARNINGS
parser_type: YAML
{_SCHEMA_KEY_KEY}: schema
{_TYPE_KEY_KEY}: type
{_DEFAULT_KEY_KEY}: default
{_CONSTRAINTS_KEY_KEY}: constraints
{_METADATA_KEY_KEY}: metadata
{_INDEX_KEY_KEY}: _index
{_MODEL_NAME_KEY}: ModelSchema
{_ALLOWED_TYPES_KEY}: [bool, int, float, str, list, date, datetime, object]
{_TYPE_ALIASES_KEY}: 
  bool: [boolean]
  int: [integer]
  float: [real, number]
  str: [string]
  object: [any]
"""

class SchemaLoader(Loader):
    """Loads and parses schemas using a configured schema parser."""

    __slots__: tuple[str, ...] = ('_manager',)

    @staticmethod
    def _get_default_settings_source() -> InlineSource:
        settings: InlineSourceSettings = InlineSourceSettings(
            content_type=ContentType.YAML, 
            content=SCHEMA_PARSER_SETTINGS
            )
        return InlineSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        super().__init__(
            default_settings_source or self._get_default_settings_source()
        )
        self._manager: SchemaParserManager = SchemaParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: LoaderContext | None = None) -> SchemaParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalSchemaDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.YAML:
                    return YamlSchemaParserSettings(
                        schema_key=config[_SCHEMA_KEY_KEY],
                        type_key=config[_TYPE_KEY_KEY],
                        default_key=config[_DEFAULT_KEY_KEY],
                        constraints_key=config[_CONSTRAINTS_KEY_KEY],
                        model_name=config[_MODEL_NAME_KEY],
                        metadata_key=config[_METADATA_KEY_KEY],
                        index_key=config[_INDEX_KEY_KEY],
                        allowed_types=tuple(config[_ALLOWED_TYPES_KEY]),
                        type_aliases=config.get(_TYPE_ALIASES_KEY, {}),
                        policy=self._load_diagnostic_policy(config, IllegalSchemaDefinitionError)
                    )
        except KeyError as e:
            raise IllegalSchemaDefinitionError(f"Missing required key in schema config: {e}") from e

        raise UnsupportedSchemaParserError(parser_type)

    def _create_settings(self, parser_settings_source: Source | None = None) -> SchemaParserSettings:
        parser_settings: ParserSettings = (
            self._default_settings
            if parser_settings_source is None
            else self._load_parser_settings(parser_settings_source)
        )

        assert isinstance(parser_settings, SchemaParserSettings)
        return parser_settings

    def load(self, schema_source: Source, parser_settings_source: Source | None = None) -> Schema:
        """Load and parse a schema from a source using the specified parser settings."""

        parser_settings: SchemaParserSettings = self._create_settings(parser_settings_source)
        parser: SchemaParser = self._manager.get_or_create(parser_settings)
        return parser.parse(schema_source.read())