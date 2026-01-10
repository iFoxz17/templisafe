from overrides import overrides
from typing import Any
from jinja2 import Environment
from dataclasses import dataclass

from templisafe.template.template_model import Template
from templisafe.loader.template.template_parser import TemplateParser
from templisafe.source.source import Source
from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_settings import InlineSourceSettings
from templisafe.settings.parser.parser_settings import ParserSettings
from templisafe.settings.parser.template_parser_settings import JinjaTemplateParserSettings, TemplateParserSettings
from templisafe.loader.template.template_parser_manager import TemplateParserManager
from templisafe.util.util import ContentType
from templisafe.exceptions.template_error import (
    QTemplateParserCreationError,
    UnsupportedQTemplateParserError, 
    IllegalQTemplateDefinitionError
)
from templisafe.loader.loader import Loader, LoaderContext

@dataclass(frozen=True, slots=True)
class JinjaTemplateLoaderContext(LoaderContext):
    env: Environment

TEMPLATE_PARSER_SETTINGS: str = """
default_diagnostic_policy: RAISE_WARNINGS
parser_type: JINJA
"""

class TemplateLoader(Loader):
    """Loads and parses templates using a configured template parser and context."""

    __slots__: tuple[str, ...] = ('_env', '_template_manager')

    @staticmethod
    def _get_default_settings_source() -> InlineSource:
        settings: InlineSourceSettings = InlineSourceSettings(
            content_type=ContentType.JINJA, 
            content=TEMPLATE_PARSER_SETTINGS
            )
        return InlineSource(settings)

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
        config: dict[str, Any] = self._load_config(raw, IllegalQTemplateDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.JINJA:
                    env: Environment = self._env
                    if context is not None:
                        if not isinstance(context, JinjaTemplateLoaderContext):
                            raise QTemplateParserCreationError(
                                parser_type=ContentType.JINJA,
                                expected_context=JinjaTemplateLoaderContext,
                                actual_context=context,
                            )
                        env = context.env
                    return JinjaTemplateParserSettings(
                        environment=env,
                        policy=self._load_diagnostic_policy(config, IllegalQTemplateDefinitionError)
                    )
        except KeyError as e:
            raise IllegalQTemplateDefinitionError(f"Missing required key in template config: {e}") from e
        
        raise UnsupportedQTemplateParserError(parser_type)

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
            ) -> Template:
        """Load and parse a template from a source using the specified parser settings."""

        parser_settings: TemplateParserSettings = self._create_settings(parser_settings_source, context)
        parser: TemplateParser = self._template_manager.get_or_create(parser_settings)
        return parser.parse(template_source.read())