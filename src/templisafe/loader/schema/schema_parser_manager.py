from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.loader.schema.schema_parser import SchemaParser

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SchemaParserFactory:
    """Creates SchemaParser instances from schema parser settings."""

    __slots__: tuple[str, ...] = ()
    
    def __init__(self) -> None:
        pass

    def create(self, settings: SchemaParserSettings) -> SchemaParser:
        """Create a SchemaParser instance for the given settings."""

        return SchemaParser(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SchemaParserManager:
    """Manages cached SchemaParser instances by their configuration settings."""

    __slots__: tuple[str, ...] = ("_default_parser_settings", "_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[SchemaParserSettings, SchemaParser] | None = None
                 ) -> None:
        self._factory: SchemaParserFactory = SchemaParserFactory()
        self._parsers: dict[SchemaParserSettings, SchemaParser] = parsers or {}

    def get_or_create(self, settings: SchemaParserSettings) -> SchemaParser:
        """Return a cached parser for the settings, creating one if needed."""

        parsers: dict[SchemaParserSettings, SchemaParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: SchemaParserSettings) -> bool:
        return settings in self._parsers