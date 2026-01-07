from jinja2 import Environment, meta
from jinja2.nodes import Template
from overrides import overrides

from sqltemplater.loader.template.qtemplate_parser import QTemplateParser
from sqltemplater.query.query_model import QTemplate
from sqltemplater.settings.parser.qtemplate_parser_settings import JinjaQTemplateParserSettings

class JinjaQTemplateParser(QTemplateParser):
    """Parses SQL templates using a Jinja2 environment and extracts variables."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, settings: JinjaQTemplateParserSettings) -> None:
        super().__init__(settings)
        self._env: Environment = settings.environment

    @overrides
    def parse(self, template_str: str) -> QTemplate:
        """Parse a template string and extract its undeclared variables as a QTemplate."""

        parsed: Template = self._env.parse(template_str)
        variables: set[str] = meta.find_undeclared_variables(parsed)
        return QTemplate(template=template_str, vars=variables)
