from overrides import overrides
from typing import Any

from templisafe.engine.template_engine import TemplateEngine
from templisafe.template.template_model import Template
from templisafe.loader.template.template_parser import TemplateParser
from templisafe.source.source import Source
from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_settings import InlineSourceSettings
from templisafe.settings.parser.template_parser_settings import TemplateParserSettings
from templisafe.util.util import ContentType
from templisafe.exceptions.template_error import IllegalQTemplateDefinitionError
from templisafe.loader.loader import Loader, LoaderContext

TEMPLATE_PARSER_SETTINGS: str = """
default_diagnostic_policy: RAISE_WARNINGS
"""

class TemplateLoader(Loader):
    """Loads and parses templates using a configured template parser and context."""

    __slots__: tuple[str, ...] = ('_engine', '_parser')

    @staticmethod
    def _get_default_settings_source() -> InlineSource:
        settings: InlineSourceSettings = InlineSourceSettings(
            content_type=ContentType.YAML, 
            content=TEMPLATE_PARSER_SETTINGS
            )
        return InlineSource(settings)

    def __init__(self, 
                 default_engine: TemplateEngine,
                 default_settings_source: Source | None = None
                 ) -> None:
        super().__init__(
            default_settings_source or self._get_default_settings_source()
        )
        self._engine: TemplateEngine = default_engine
        assert isinstance(self._default_settings, TemplateParserSettings)
        self._parser: TemplateParser = TemplateParser(self._default_settings)

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: LoaderContext | None = None) -> TemplateParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalQTemplateDefinitionError)
        return TemplateParserSettings(
            policy=self._load_diagnostic_policy(config, IllegalQTemplateDefinitionError)
        )
        
    def load(
            self, 
            template_source: Source, 
            engine: TemplateEngine | None = None
            ) -> Template:
        """Load and parse a template from a source using the specified parser settings."""

        engine_to_use: TemplateEngine = engine or self._engine
        template_str: str = template_source.read()
        vars: set[str] = engine_to_use.extract_variables(template_str)
        return self._parser.parse(template_str, vars)