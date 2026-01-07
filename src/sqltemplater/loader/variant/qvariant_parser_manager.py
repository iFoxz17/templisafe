from sqltemplater.settings.parser.qparams_parser_settings import QVariantParserSettings, YamlQVariantParserSettings
from sqltemplater.loader.variant.qvariant_parser import QVariantParser
from sqltemplater.loader.variant.yaml_qvariant_parser import YamlQVariantParser
from sqltemplater.exceptions.binding_error import UnsupportedQVariantParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class QVariantParserFactory:

    __slots__: tuple[str, ...] = ()

    _PARSER_MAP: dict[type[QVariantParserSettings], type[QVariantParser]] = {
        YamlQVariantParserSettings: YamlQVariantParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: QVariantParserSettings) -> QVariantParser:

        type_: type[QVariantParserSettings] = type(settings)
        parser_type: type[QVariantParser] | None = QVariantParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnsupportedQVariantParserError(settings.content_type)
        return parser_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class QVariantParserManager:
    __slots__: tuple[str, ...] = ("_default_parser_settings", "_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[QVariantParserSettings, QVariantParser] | None = None
                 ) -> None:
        self._factory: QVariantParserFactory = QVariantParserFactory()
        self._parsers: dict[QVariantParserSettings, QVariantParser] = parsers or {}

    def get_or_create(self, settings: QVariantParserSettings) -> QVariantParser:
        parsers: dict[QVariantParserSettings, QVariantParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: QVariantParserSettings) -> bool:
        return settings in self._parsers