from typing import Any, Iterable
from abc import ABC, abstractmethod

from sqltemplater.loader.parser import Parser
from sqltemplater.settings.parser.template_parser_settings import TemplateParserSettings
from sqltemplater.query.query_model import QueryTemplate

class TemplateParser(Parser, ABC):
    """
    Abstract base class for parsing and validating sql templates.
    """

    def __init__(self, settings: TemplateParserSettings) -> None:
        super().__init__(settings)
                
    @abstractmethod
    def parse(self, template_str: str) -> QueryTemplate:
        pass    
