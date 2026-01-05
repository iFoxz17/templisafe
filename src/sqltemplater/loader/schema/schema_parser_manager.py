from sqltemplater.settings.parser.schema_parser_settings import SchemaParserSettings, YamlSchemaParserSettings
from sqltemplater.loader.schema.schema_parser import SchemaParser
from sqltemplater.loader.schema.yaml_schema_parser import YamlSchemaParser
from sqltemplater.exceptions.schema_error import UnimplementedSchemaParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SchemaParserFactory:
    """
    Factory class to create SchemaParser instances from a YAML configuration file.
    """

    _PARSER_MAP: dict[type[SchemaParserSettings], type[SchemaParser]] = {
        YamlSchemaParserSettings: YamlSchemaParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: SchemaParserSettings) -> SchemaParser:
        """
        Create a SchemaParser instance based on the given configuration.
        """

        type_: type[SchemaParserSettings] = type(settings)
        parser_type: type[SchemaParser] | None = SchemaParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnimplementedSchemaParserError(settings.content_type)
        return parser_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SchemaParserManager:
    __slots__ = ("_default_parser_settings", "_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[SchemaParserSettings, SchemaParser] | None = None
                 ) -> None:
        self._factory: SchemaParserFactory = SchemaParserFactory()
        self._parsers: dict[SchemaParserSettings, SchemaParser] = parsers or {}

    def get_or_create(self, settings: SchemaParserSettings) -> SchemaParser:
        parsers: dict[SchemaParserSettings, SchemaParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: SchemaParserSettings) -> bool:
        return settings in self._parsers