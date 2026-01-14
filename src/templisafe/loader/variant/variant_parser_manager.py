from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.loader.variant.variant_parser import VariantParser

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class VariantParserFactory:

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def create(self, settings: VariantParserSettings) -> VariantParser:
        return VariantParser(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class VariantParserManager:
    __slots__: tuple[str, ...] = ("_default_parser_settings", "_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[VariantParserSettings, VariantParser] | None = None
                 ) -> None:
        self._factory: VariantParserFactory = VariantParserFactory()
        self._parsers: dict[VariantParserSettings, VariantParser] = parsers or {}

    def get_or_create(self, settings: VariantParserSettings) -> VariantParser:
        parsers: dict[VariantParserSettings, VariantParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: VariantParserSettings) -> bool:
        return settings in self._parsers