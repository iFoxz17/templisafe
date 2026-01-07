from sqltemplater.settings.parser.qschema_parser_settings import QSchemaParserSettings, YamlQSchemaParserSettings
from sqltemplater.loader.schema.qschema_parser import QSchemaParser
from sqltemplater.loader.schema.yaml_qschema_parser import QYamlSchemaParser
from sqltemplater.exceptions.schema_error import UnimplementedSchemaParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class QSchemaParserFactory:
    """Creates SchemaParser instances from schema parser settings."""

    __slots__: tuple[str, ...] = ()

    _PARSER_MAP: dict[type[QSchemaParserSettings], type[QSchemaParser]] = {
        YamlQSchemaParserSettings: QYamlSchemaParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: QSchemaParserSettings) -> QSchemaParser:
        """Create a SchemaParser instance for the given settings."""

        type_: type[QSchemaParserSettings] = type(settings)
        parser_type: type[QSchemaParser] | None = QSchemaParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnimplementedSchemaParserError(settings.content_type)
        return parser_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class QSchemaParserManager:
    """Manages cached SchemaParser instances by their configuration settings."""

    __slots__: tuple[str, ...] = ("_default_parser_settings", "_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[QSchemaParserSettings, QSchemaParser] | None = None
                 ) -> None:
        self._factory: QSchemaParserFactory = QSchemaParserFactory()
        self._parsers: dict[QSchemaParserSettings, QSchemaParser] = parsers or {}

    def get_or_create(self, settings: QSchemaParserSettings) -> QSchemaParser:
        """Return a cached parser for the settings, creating one if needed."""

        parsers: dict[QSchemaParserSettings, QSchemaParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: QSchemaParserSettings) -> bool:
        return settings in self._parsers