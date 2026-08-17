from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------


class VariantParserFactory:
    """Creates `VariantParser` instances from variant parser settings."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def create(self, settings: VariantParserSettings) -> VariantParser:
        """Create a `VariantParser` instance for the given settings."""

        return VariantParser(settings)


# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------


class VariantParserManager:
    """Manages cached `VariantParser` instances by their configuration settings."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_parsers")

    def __init__(
        self,
        settings: ManagerSettings,
        factory: VariantParserFactory | None = None,
        parsers: dict[VariantParserSettings, VariantParser] | None = None,
    ) -> None:
        self._settings: ManagerSettings = settings
        self._factory: VariantParserFactory = factory or VariantParserFactory()
        self._parsers: dict[VariantParserSettings, VariantParser] = parsers or {}

    def get_or_create(self, settings: VariantParserSettings) -> VariantParser:
        """Return a `VariantParser` instance according to the given settings."""

        s: dict[VariantParserSettings, VariantParser] = self._parsers
        if settings in s:
            return s[settings]

        variant_parser: VariantParser = self._factory.create(settings)
        if self._settings.cache:
            s[settings] = variant_parser
        return variant_parser

    def __contains__(self, settings: VariantParserSettings) -> bool:
        """Return whether a `VariantParser` instance for the given settings is cached."""

        return settings in self._parsers
