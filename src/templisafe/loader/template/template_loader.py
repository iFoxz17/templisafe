from templisafe.engine.template_engine import TemplateEngine
from templisafe.template.template_model import Template
from templisafe.loader.template.template_parser import TemplateParser
from templisafe.source.source import Source
from templisafe.settings.template_parser_settings import TemplateParserSettings

TEMPLATE_PARSER_SETTINGS_YAML: str = """{}
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
            template_str: str, 
            engine: TemplateEngine | None = None
            ) -> Template:
        """Load and parse a template from a source using the specified parser settings."""

        engine_to_use: TemplateEngine = engine or self._engine
        vars: set[str] = engine_to_use.extract_variables(template_str)
        return self._parser.parse(template_str, vars)