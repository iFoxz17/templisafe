from overrides import overrides
from typing import Any

from templisafe.engine.template_engine import TemplateEngine
from templisafe.template.template_model import Template
from templisafe.loader.template.template_parser import TemplateParser
from templisafe.source.source import Source
from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_settings import InlineSourceSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.util.util import ContentType
from templisafe.exceptions.template_error import IllegalQTemplateDefinitionError

TEMPLATE_PARSER_SETTINGS_YAML: str = """
default_diagnostic_policy: RAISE_WARNINGS
"""

class TemplateLoader:
    """Loads and parses templates using a configured template parser and context."""

    __slots__: tuple[str, ...] = ('_default_settings', '_engine', '_parser')

    def __init__(self, 
                 default_engine: TemplateEngine,
                 default_settings: TemplateParserSettings | None = None
                 ) -> None:
        self._default_settings: TemplateParserSettings = default_settings or TemplateParserSettings.from_yaml(TEMPLATE_PARSER_SETTINGS_YAML) 
        self._engine: TemplateEngine = default_engine
        self._parser: TemplateParser = TemplateParser(self._default_settings)
    
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