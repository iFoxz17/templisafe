from abc import ABC
from overrides import overrides
from jinja2 import Environment

from sqltemplater.util.util import ContentType
from sqltemplater.settings.parser.qparser_settings import QParserSettings

class QTemplateParserSettings(QParserSettings, ABC):

    model_config = {
        "frozen": True,
        "arbitrary_types_allowed": True
    }

class JinjaQTemplateParserSettings(QTemplateParserSettings):
    environment: Environment

    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.JINJA 

    model_config = {
        "frozen": True
    }