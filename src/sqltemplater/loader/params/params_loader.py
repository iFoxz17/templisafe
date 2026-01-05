from overrides import overrides
from typing import Any

from sqltemplater.query.query_model import QueryParameterization
from sqltemplater.loader.params.params_parser import ParamsParser
from sqltemplater.source.source import Source
from sqltemplater.source.content_source import ContentSource
from sqltemplater.settings.source_settings import ContentSourceSettings
from sqltemplater.loader.params.params_parser_manager import ParamsParserManager
from sqltemplater.loader.loader import Loader, LoaderContext
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.settings.parser.params_parser_settings import YamlParamsParserSettings, ParamsParserSettings
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.params_error import IllegalParamsDefinitionError, UnimplementedParamsParserError

PARAMS_PARSER_SETTINGS: str = f"""
default_diagnostic_policy: RAISE_WARNINGS
parser_type: YAML
params_key: params
default_parameterization_name: parameterization
"""

class ParamsLoader(Loader):

    _PARAMS_KEY_KEY: str = 'params_key'
    _DEFAULT_PARAMETERIZATION_KEY_KEY: str = 'default_parameterization_name'

    __slots__ = ('_manager')

    @staticmethod
    def _get_default_settings_source() -> ContentSource:
        settings: ContentSourceSettings = ContentSourceSettings(ContentType.YAML, PARAMS_PARSER_SETTINGS)
        return ContentSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        super().__init__(
            default_settings_source or ParamsLoader._get_default_settings_source()
        )
        self._manager: ParamsParserManager = ParamsParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: LoaderContext | None = None) -> ParamsParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalParamsDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.YAML:
                    return YamlParamsParserSettings(
                        params_key=config[ParamsLoader._PARAMS_KEY_KEY],
                        default_parameterization_name=config[ParamsLoader._DEFAULT_PARAMETERIZATION_KEY_KEY]
                    )
        except KeyError as e:
            raise IllegalParamsDefinitionError(f"Missing required key in params config: {e}") from e

        raise UnimplementedParamsParserError(parser_type)

    def _create_settings(self, parser_settings_source: Source | None = None) -> ParamsParserSettings:
        parser_settings: ParserSettings = (
            self._default_settings 
            if parser_settings_source is None 
            else self._load_parser_settings(parser_settings_source)
        ) 
        
        assert isinstance(parser_settings, ParamsParserSettings)
        return parser_settings

    def load(self, params_source: Source, parser_settings_source: Source | None = None) -> QueryParameterization:
        parser_settings: ParamsParserSettings = self._create_settings(parser_settings_source)
        parser: ParamsParser = self._manager.get_or_create(parser_settings)
        return parser.parse(params_source.read())