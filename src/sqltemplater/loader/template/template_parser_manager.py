from sqltemplater.settings.parser.template_parser_settings import TemplateParserSettings, JinjaTemplateParserSettings
from sqltemplater.loader.template.template_parser import TemplateParser
from sqltemplater.loader.template.jinja_template_parser import JinjaTemplateParser
from sqltemplater.exceptions.template_error import UnimplementedTemplateParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class TemplateParserFactory:
    """
    Factory class to create TemplateParser instances from a YAML configuration file.
    """

    _PARSER_MAP: dict[type[TemplateParserSettings], type[TemplateParser]] = {
        JinjaTemplateParserSettings: JinjaTemplateParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: TemplateParserSettings) -> TemplateParser:
        """
        Create a TemplateParser instance based on the given configuration.
        """

        type_: type[TemplateParserSettings] = type(settings)
        parser_type: type[TemplateParser] | None = TemplateParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnimplementedTemplateParserError(settings.content_type)
        return parser_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class TemplateParserManager:
    __slots__ = ("_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[TemplateParserSettings, TemplateParser] | None = None
                 ) -> None:
        self._factory: TemplateParserFactory = TemplateParserFactory()
        self._parsers: dict[TemplateParserSettings, TemplateParser] = parsers or {}

    def get_or_create(self, settings: TemplateParserSettings) -> TemplateParser:
        parsers: dict[TemplateParserSettings, TemplateParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: TemplateParserSettings) -> bool:
        return settings in self._parsers
