from abc import ABC
from overrides import overrides
from jinja2 import Environment

from templisafe.util.util import ContentType
from templisafe.settings.parser.parser_settings import ParserSettings

class TemplateParserSettings(ParserSettings, ABC):

    model_config = {
        "frozen": True,
        "arbitrary_types_allowed": True
    }

class JinjaTemplateParserSettings(TemplateParserSettings):
    environment: Environment

    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.JINJA 

    model_config = {
        "frozen": True
    }