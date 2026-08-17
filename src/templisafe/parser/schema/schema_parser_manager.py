from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------


class SchemaParserFactory:
    """Creates `SchemaParser` instances from schema parser settings."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def create(self, settings: SchemaParserSettings) -> SchemaParser:
        """Create a `SchemaParser` instance for the given settings."""

        return SchemaParser(settings)


# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------


class SchemaParserManager:
    """Manages cached `SchemaParser` instances by their configuration settings."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_parsers")

    def __init__(
        self,
        settings: ManagerSettings,
        factory: SchemaParserFactory | None = None,
        parsers: dict[SchemaParserSettings, SchemaParser] | None = None,
    ) -> None:
        self._settings: ManagerSettings = settings
        self._factory: SchemaParserFactory = factory or SchemaParserFactory()
        self._parsers: dict[SchemaParserSettings, SchemaParser] = parsers or {}

    def get_or_create(self, settings: SchemaParserSettings) -> SchemaParser:
        """Return a `SchemaParser` instance according to the given settings."""

        s: dict[SchemaParserSettings, SchemaParser] = self._parsers
        if settings in s:
            return s[settings]

        schema_parser: SchemaParser = self._factory.create(settings)
        if self._settings.cache:
            s[settings] = schema_parser
        return schema_parser

    def __contains__(self, settings: SchemaParserSettings) -> bool:
        """Return whether a `SchemaParser` instance for the given settings is cached."""

        return settings in self._parsers
