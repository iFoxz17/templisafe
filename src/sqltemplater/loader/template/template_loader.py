from overrides import overrides
from typing import Any
from jinja2 import Environment
from dataclasses import dataclass

from sqltemplater.query.query_model import QueryTemplate
from sqltemplater.loader.template.template_parser import TemplateParser
from sqltemplater.source.source import Source
from sqltemplater.source.content_source import ContentSource
from sqltemplater.settings.source_settings import ContentSourceSettings
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.settings.parser.template_parser_settings import JinjaTemplateParserSettings, TemplateParserSettings
from sqltemplater.loader.template.template_parser_manager import TemplateParserManager
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.template_error import (
    TemplateParserCreationError,
    UnimplementedTemplateParserError, 
    IllegalTemplateDefinitionError
)
from sqltemplater.loader.loader import Loader, LoaderContext

@dataclass(frozen=True, slots=True)
class JinjaTemplateLoaderContext(LoaderContext):
    env: Environment

TEMPLATE_PARSER_SETTINGS: str = """
default_diagnostic_policy: RAISE_WARNINGS
parser_type: JINJA
"""

class TemplateLoader(Loader):

    __slots__ = ('_env', '_template_manager')

    @staticmethod
    def _get_default_settings_source() -> ContentSource:
        settings: ContentSourceSettings = ContentSourceSettings(ContentType.JINJA, TEMPLATE_PARSER_SETTINGS)
        return ContentSource(settings)

    def __init__(self, 
                 default_env: Environment,
                 default_settings_source: Source | None = None
                 ) -> None:
        self._env: Environment = default_env    
        super().__init__(
            default_settings_source or TemplateLoader._get_default_settings_source()
        )
        self._template_manager: TemplateParserManager = TemplateParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: LoaderContext | None = None) -> TemplateParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalTemplateDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.JINJA:
                    env: Environment = self._env
                    if context is not None:
                        if not isinstance(context, JinjaTemplateLoaderContext):
                            raise TemplateParserCreationError(
                                parser_type=ContentType.JINJA,
                                expected_context=JinjaTemplateLoaderContext,
                                actual_context=context,
                            )
                        env = context.env
                    return JinjaTemplateParserSettings(
                        environment=env,
                        policy=self._load_diagnostic_policy(config, IllegalTemplateDefinitionError)
                    )
        except KeyError as e:
            raise IllegalTemplateDefinitionError(f"Missing required key in template config: {e}") from e
        
        raise UnimplementedTemplateParserError(parser_type)

    def _create_settings(
            self, 
            parser_settings_source: Source | None = None,
            context: LoaderContext | None = None
            ) -> TemplateParserSettings:
        parser_settings: ParserSettings = (
            self._default_settings if parser_settings_source is None
            else self._load_parser_settings(parser_settings_source, context)
        )
        
        assert isinstance(parser_settings, TemplateParserSettings)
        return parser_settings

    def load(
            self, 
            template_source: Source, 
            context: LoaderContext | None = None,            
            parser_settings_source: Source | None = None
            ) -> QueryTemplate:
        parser_settings: TemplateParserSettings = self._create_settings(parser_settings_source, context)
        parser: TemplateParser = self._template_manager.get_or_create(parser_settings)
        return parser.parse(template_source.read())