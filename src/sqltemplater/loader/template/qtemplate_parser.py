from abc import ABC, abstractmethod

from sqltemplater.loader.qparser import QParser
from sqltemplater.settings.parser.qtemplate_parser_settings import QTemplateParserSettings
from sqltemplater.query.query_model import QTemplate

class QTemplateParser(QParser, ABC):
    """Abstract base class for parsing and validating SQL templates."""

    def __init__(self, settings: QTemplateParserSettings) -> None:
        """Initialize the parser with the given template parser settings."""
        super().__init__(settings)
                
    @abstractmethod
    def parse(self, template_str: str) -> QTemplate:
        """Parse a template string and return a QTemplate with its variables."""
