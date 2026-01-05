from overrides import overrides
from typing import Any

from sqltemplater.query.query_model import QuerySchema
from sqltemplater.loader.schema.schema_parser import SchemaParser
from sqltemplater.source.source import Source
from sqltemplater.source.content_source import ContentSource
from sqltemplater.settings.source_settings import ContentSourceSettings
from sqltemplater.loader.schema.schema_parser_manager import SchemaParserManager
from sqltemplater.loader.loader import Loader, LoaderContext
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings, SchemaParserSettings
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.schema_error import IllegalSchemaDefinitionError, UnimplementedSchemaParserError

SCHEMA_PARSER_SETTINGS: str = """
default_diagnostic_policy: RAISE_WARNINGS
parser_type: YAML
schema_key: schema
type_key: type
default_key: default
allowed_types: [bool, int, float, real, str, list, object]
type_aliases: 
  bool: [boolean]
  int: [integer]
  real: [number]
  str: [string]
  object: [any]
"""

class SchemaLoader(Loader):

    _SCHEMA_KEY_KEY: str = 'schema_key'
    _TYPE_KEY_KEY: str = 'type_key'
    _DEFAULT_KEY_KEY: str = 'default_key'
    _ALLOWED_TYPES_KEY: str = 'allowed_types'
    _TYPE_ALIASES_KEY: str = 'type_aliases'

    __slots__ = ('_manager')

    @staticmethod
    def _get_default_settings_source() -> ContentSource:
        settings: ContentSourceSettings = ContentSourceSettings(ContentType.YAML, SCHEMA_PARSER_SETTINGS)
        return ContentSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        super().__init__(
            default_settings_source or SchemaLoader._get_default_settings_source()
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
                        schema_key=config[SchemaLoader._SCHEMA_KEY_KEY],
                        type_key=config[SchemaLoader._TYPE_KEY_KEY],
                        default_key=config[SchemaLoader._DEFAULT_KEY_KEY],
                        allowed_types=tuple(config[SchemaLoader._ALLOWED_TYPES_KEY]),
                        type_aliases=config.get(SchemaLoader._TYPE_ALIASES_KEY, {}),
                        policy=self._load_diagnostic_policy(config, IllegalSchemaDefinitionError)
                    )
        except KeyError as e:
            raise IllegalSchemaDefinitionError(f"Missing required key in schema config: {e}") from e

        raise UnimplementedSchemaParserError(parser_type)

    def _create_settings(self, parser_settings_source: Source | None = None) -> SchemaParserSettings:
        parser_settings: ParserSettings = (
            self._default_settings
            if parser_settings_source is None
            else self._load_parser_settings(parser_settings_source)
        )

        assert isinstance(parser_settings, SchemaParserSettings)
        return parser_settings

    def load(self, schema_source: Source, parser_settings_source: Source | None = None) -> QuerySchema:
        parser_settings: SchemaParserSettings = self._create_settings(parser_settings_source)
        parser: SchemaParser = self._manager.get_or_create(parser_settings)
        return parser.parse(schema_source.read())