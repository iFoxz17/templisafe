from overrides import overrides
from typing import Any

from sqltemplater.query.query_model import QSchema
from sqltemplater.loader.schema.qschema_parser import QSchemaParser
from sqltemplater.source.source import Source
from sqltemplater.source.content_source import ContentSource
from sqltemplater.settings.source_settings import ContentSourceSettings
from sqltemplater.loader.schema.qschema_parser_manager import QSchemaParserManager
from sqltemplater.loader.qloader import QLoader, QLoaderContext
from sqltemplater.settings.parser.qparser_settings import QParserSettings
from sqltemplater.settings.parser.qschema_parser_settings import YamlQSchemaParserSettings, QSchemaParserSettings
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

class QSchemaLoader(QLoader):
    """Loads and parses schemas using a configured schema parser."""

    _SCHEMA_KEY_KEY: str = 'schema_key'
    _TYPE_KEY_KEY: str = 'type_key'
    _DEFAULT_KEY_KEY: str = 'default_key'
    _ALLOWED_TYPES_KEY: str = 'allowed_types'
    _TYPE_ALIASES_KEY: str = 'type_aliases'

    __slots__: tuple[str, ...] = ('_manager',)

    @staticmethod
    def _get_default_settings_source() -> ContentSource:
        settings: ContentSourceSettings = ContentSourceSettings(ContentType.YAML, SCHEMA_PARSER_SETTINGS)
        return ContentSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        super().__init__(
            default_settings_source or QSchemaLoader._get_default_settings_source()
        )
        self._manager: QSchemaParserManager = QSchemaParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: QLoaderContext | None = None) -> QSchemaParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalSchemaDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.YAML:
                    return YamlQSchemaParserSettings(
                        schema_key=config[QSchemaLoader._SCHEMA_KEY_KEY],
                        type_key=config[QSchemaLoader._TYPE_KEY_KEY],
                        default_key=config[QSchemaLoader._DEFAULT_KEY_KEY],
                        allowed_types=tuple(config[QSchemaLoader._ALLOWED_TYPES_KEY]),
                        type_aliases=config.get(QSchemaLoader._TYPE_ALIASES_KEY, {}),
                        policy=self._load_diagnostic_policy(config, IllegalSchemaDefinitionError)
                    )
        except KeyError as e:
            raise IllegalSchemaDefinitionError(f"Missing required key in schema config: {e}") from e

        raise UnimplementedSchemaParserError(parser_type)

    def _create_settings(self, parser_settings_source: Source | None = None) -> QSchemaParserSettings:
        parser_settings: QParserSettings = (
            self._default_settings
            if parser_settings_source is None
            else self._load_parser_settings(parser_settings_source)
        )

        assert isinstance(parser_settings, QSchemaParserSettings)
        return parser_settings

    def load(self, schema_source: Source, parser_settings_source: Source | None = None) -> QSchema:
        """Load and parse a schema from a source using the specified parser settings."""

        parser_settings: QSchemaParserSettings = self._create_settings(parser_settings_source)
        parser: QSchemaParser = self._manager.get_or_create(parser_settings)
        return parser.parse(schema_source.read())