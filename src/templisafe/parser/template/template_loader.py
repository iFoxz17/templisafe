from templisafe.engine.template_engine import TemplateEngine
from templisafe.template.template_model import Template
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.settings.template_parser_settings import TemplateParserSettings

TEMPLATE_PARSER_SETTINGS_YAML: str = """{}
"""

class TemplateLoader:
    """Loads and parses templates using a configured template parser and context."""

    __slots__: tuple[str, ...] = ('_default_settings', '_parser')

    def __init__(self, 
                 default_settings: TemplateParserSettings | None = None
                 ) -> None:
        self._default_settings: TemplateParserSettings = default_settings or TemplateParserSettings.from_yaml(TEMPLATE_PARSER_SETTINGS_YAML) 
        self._parser: TemplateParser = TemplateParser(self._default_settings)
    
    def load(
            self, 
            template_str: str, 
            engine: TemplateEngine,
            parser_settings: TemplateParserSettings | None = None
            ) -> Template:
        """Load and parse a template from a source using the specified parser settings."""

        vars: set[str] = engine.extract_variables(template_str)
        return self._parser.parse(template_str, vars)