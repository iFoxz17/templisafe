from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.template.template_model import Template

class TemplateParser:
    """Creates `Template` instances from the template strings anf the template variables names."""

    __slots__: tuple[str, ...] = ('_settings',)

    def __init__(self, settings: TemplateParserSettings) -> None:
        self._settings: TemplateParserSettings = settings
                
    def parse(self, template_str: str, vars: set[str]) -> Template:
        """Return a `Template` with its variables."""
        return Template(template_str=template_str, vars=vars)


