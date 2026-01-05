from abc import ABC
from overrides import overrides

from sqltemplater.util.util import ContentType
from sqltemplater.settings.parser.parser_settings import ParserSettings

class ParamsParserSettings(ParserSettings, ABC):
    params_key: str
    default_parameterization_name: str
    
    model_config = {
        "frozen": True
    }

class YamlParamsParserSettings(ParamsParserSettings):
    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.YAML

