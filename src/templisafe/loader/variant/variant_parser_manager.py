from templisafe.settings.parser.variant_parser_settings import VariantParserSettings, YamlVariantParserSettings
from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.loader.variant.yaml_variant_parser import YamlVariantParser
from templisafe.exceptions.binding_error import UnsupportedQVariantParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class VariantParserFactory:

    __slots__: tuple[str, ...] = ()

    _PARSER_MAP: dict[type[VariantParserSettings], type[VariantParser]] = {
        YamlVariantParserSettings: YamlVariantParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: VariantParserSettings) -> VariantParser:

        type_: type[VariantParserSettings] = type(settings)
        parser_type: type[VariantParser] | None = VariantParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnsupportedQVariantParserError(settings.content_type)
        return parser_type(settings)

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