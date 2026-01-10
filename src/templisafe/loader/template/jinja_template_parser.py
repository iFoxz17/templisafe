from jinja2 import Environment, meta
from jinja2.nodes import Template as JTemplate
from overrides import overrides

from templisafe.loader.template.template_parser import TemplateParser
from templisafe.template.template_model import Template
from templisafe.settings.parser.template_parser_settings import JinjaTemplateParserSettings

class JinjaTemplateParser(TemplateParser):
    """Parses SQL templates using a Jinja2 environment and extracts variables."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, settings: JinjaTemplateParserSettings) -> None:
        super().__init__(settings)
        self._env: Environment = settings.environment

    @overrides
    def parse(self, template_str: str) -> Template:
        """Parse a template string and extract its undeclared variables as a Template."""

        parsed: JTemplate = self._env.parse(template_str)
        vars: set[str] = meta.find_undeclared_variables(parsed)
        return Template(template=template_str, vars=vars)
