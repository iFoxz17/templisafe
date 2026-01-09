from abc import ABC, abstractmethod

from sqltemplater.loader.parser import Parser
from sqltemplater.settings.parser.template_parser_settings import TemplateParserSettings
from sqltemplater.template.template_model import Template

class TemplateParser(Parser, ABC):
    """Abstract base class for parsing and validating SQL templates."""

    def __init__(self, settings: TemplateParserSettings) -> None:
        """Initialize the parser with the given template parser settings."""
        super().__init__(settings)
                
    @abstractmethod
    def parse(self, template_str: str) -> Template:
        """Parse a template string and return a Template with its variables."""
