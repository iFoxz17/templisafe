from sqltemplater.settings.parser.params_parser_settings import ParamsParserSettings, YamlParamsParserSettings
from sqltemplater.loader.params.params_parser import ParamsParser
from sqltemplater.loader.params.yaml_params_parser import YamlParamsParser
from sqltemplater.exceptions.params_error import UnimplementedParamsParserError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class ParamsParserFactory:
    """
    Factory class to create ParamsParser instances from a YAML configuration file.
    """

    _PARSER_MAP: dict[type[ParamsParserSettings], type[ParamsParser]] = {
        YamlParamsParserSettings: YamlParamsParser
    }
    
    def __init__(self) -> None:
        pass

    def create(self, settings: ParamsParserSettings) -> ParamsParser:
        """
        Create a ParamsParser instance based on the given configuration.
        """

        type_: type[ParamsParserSettings] = type(settings)
        parser_type: type[ParamsParser] | None = ParamsParserFactory._PARSER_MAP.get(type_)
        if parser_type is None:
            raise UnimplementedParamsParserError(settings.content_type)
        return parser_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class ParamsParserManager:
    __slots__ = ("_default_parser_settings", "_factory", "_parsers")
    
    def __init__(self, 
                 parsers: dict[ParamsParserSettings, ParamsParser] | None = None
                 ) -> None:
        self._factory: ParamsParserFactory = ParamsParserFactory()
        self._parsers: dict[ParamsParserSettings, ParamsParser] = parsers or {}

    def get_or_create(self, settings: ParamsParserSettings) -> ParamsParser:
        parsers: dict[ParamsParserSettings, ParamsParser] = self._parsers    
        if settings not in parsers:
            parsers[settings] = self._factory.create(settings)
        return parsers[settings]
    
    def __contains__(self, settings: ParamsParserSettings) -> bool:
        return settings in self._parsers