from jinja2 import Environment, meta
from jinja2.nodes import Template
from overrides import overrides

from sqltemplater.loader.template.template_parser import TemplateParser
from sqltemplater.query.query_model import QueryTemplate
from sqltemplater.settings.parser.template_parser_settings import JinjaTemplateParserSettings

class JinjaTemplateParser(TemplateParser):

    def __init__(self, settings: JinjaTemplateParserSettings) -> None:
        super().__init__(settings)
        self._env: Environment = settings.environment

    @overrides
    def parse(self, template_str: str) -> QueryTemplate:
        parsed: Template = self._env.parse(template_str)
        variables: set[str] = meta.find_undeclared_variables(parsed)
        return QueryTemplate(template=template_str, params=variables)
