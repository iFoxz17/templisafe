from overrides import overrides
from typing import Any
from jinja2 import Environment
from dataclasses import dataclass

from sqltemplater.query.query_model import QTemplate
from sqltemplater.loader.template.qtemplate_parser import QTemplateParser
from sqltemplater.source.source import Source
from sqltemplater.source.content_source import ContentSource
from sqltemplater.settings.source_settings import ContentSourceSettings
from sqltemplater.settings.parser.qparser_settings import QParserSettings
from sqltemplater.settings.parser.qtemplate_parser_settings import JinjaQTemplateParserSettings, QTemplateParserSettings
from sqltemplater.loader.template.qtemplate_parser_manager import QTemplateParserManager
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.template_error import (
    QTemplateParserCreationError,
    UnsupportedQTemplateParserError, 
    IllegalQTemplateDefinitionError
)
from sqltemplater.loader.qloader import QLoader, QLoaderContext

@dataclass(frozen=True, slots=True)
class JinjaQTemplateLoaderContext(QLoaderContext):
    env: Environment

TEMPLATE_PARSER_SETTINGS: str = """
default_diagnostic_policy: RAISE_WARNINGS
parser_type: JINJA
"""

class QTemplateLoader(QLoader):
    """Loads and parses templates using a configured template parser and context."""

    __slots__: tuple[str, ...] = ('_env', '_template_manager')

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
            default_settings_source or QTemplateLoader._get_default_settings_source()
        )
        self._template_manager: QTemplateParserManager = QTemplateParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: QLoaderContext | None = None) -> QTemplateParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalQTemplateDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.JINJA:
                    env: Environment = self._env
                    if context is not None:
                        if not isinstance(context, JinjaQTemplateLoaderContext):
                            raise QTemplateParserCreationError(
                                parser_type=ContentType.JINJA,
                                expected_context=JinjaQTemplateLoaderContext,
                                actual_context=context,
                            )
                        env = context.env
                    return JinjaQTemplateParserSettings(
                        environment=env,
                        policy=self._load_diagnostic_policy(config, IllegalQTemplateDefinitionError)
                    )
        except KeyError as e:
            raise IllegalQTemplateDefinitionError(f"Missing required key in template config: {e}") from e
        
        raise UnsupportedQTemplateParserError(parser_type)

    def _create_settings(
            self, 
            parser_settings_source: Source | None = None,
            context: QLoaderContext | None = None
            ) -> QTemplateParserSettings:
        parser_settings: QParserSettings = (
            self._default_settings if parser_settings_source is None
            else self._load_parser_settings(parser_settings_source, context)
        )
        
        assert isinstance(parser_settings, QTemplateParserSettings)
        return parser_settings

    def load(
            self, 
            template_source: Source, 
            context: QLoaderContext | None = None,            
            parser_settings_source: Source | None = None
            ) -> QTemplate:
        """Load and parse a template from a source using the specified parser settings."""

        parser_settings: QTemplateParserSettings = self._create_settings(parser_settings_source, context)
        parser: QTemplateParser = self._template_manager.get_or_create(parser_settings)
        return parser.parse(template_source.read())