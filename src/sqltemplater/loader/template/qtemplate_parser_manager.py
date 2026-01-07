from sqltemplater.settings.parser.qtemplate_parser_settings import QTemplateParserSettings, JinjaQTemplateParserSettings
from sqltemplater.loader.template.qtemplate_parser import QTemplateParser
from sqltemplater.loader.template.jinja_qtemplate_parser import JinjaQTemplateParser
from sqltemplater.exceptions.template_error import UnsupportedQTemplateParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class QTemplateParserFactory:
    """Creates QTemplateParser instances from parser settings."""

    __slots__: tuple[str, ...] = ()

    _PARSER_MAP: dict[type[QTemplateParserSettings], type[QTemplateParser]] = {
        JinjaQTemplateParserSettings: JinjaQTemplateParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: QTemplateParserSettings) -> QTemplateParser:
        """Create a TemplateParser instance for the given settings."""

        type_: type[QTemplateParserSettings] = type(settings)
        parser_type: type[QTemplateParser] | None = QTemplateParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnsupportedQTemplateParserError(settings.content_type)
        return parser_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class QTemplateParserManager:
    """Manages cached QTemplateParser instances by their configuration settings."""

    __slots__: tuple[str, ...] = ("_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[QTemplateParserSettings, QTemplateParser] | None = None
                 ) -> None:
        self._factory: QTemplateParserFactory = QTemplateParserFactory()
        self._parsers: dict[QTemplateParserSettings, QTemplateParser] = parsers or {}

    def get_or_create(self, settings: QTemplateParserSettings) -> QTemplateParser:
        """Return a cached parser for the settings, creating one if needed."""

        parsers: dict[QTemplateParserSettings, QTemplateParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: QTemplateParserSettings) -> bool:
        return settings in self._parsers
