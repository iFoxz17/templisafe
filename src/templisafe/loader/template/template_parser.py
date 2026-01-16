from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.template.template_model import Template

class TemplateParser:
    """Abstract base class for parsing and validating SQL templates."""

    __slots__: tuple[str, ...] = ('_settings',)

    def __init__(self, settings: TemplateParserSettings) -> None:
        """Initialize the parser with the given template parser settings."""
        self._settings = settings
                
    def parse(self, template_str: str, vars: set[str]) -> Template:
        """Parse a template string and return a Template with its variables."""

        return Template(template_str=template_str, vars=vars)


