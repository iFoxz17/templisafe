from abc import ABC
from overrides import overrides

from templisafe.util.util import ContentType
from templisafe.settings.parser.parser_settings import ParserSettings

class VariantParserSettings(ParserSettings, ABC):
    variants_key: str
    default_variants_name: str
    
    model_config = {
        "frozen": True
    }

class YamlVariantParserSettings(VariantParserSettings):
    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.YAML

