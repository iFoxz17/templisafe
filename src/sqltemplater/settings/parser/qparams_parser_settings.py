from abc import ABC
from overrides import overrides

from sqltemplater.util.util import ContentType
from sqltemplater.settings.parser.qparser_settings import QParserSettings

class QVariantParserSettings(QParserSettings, ABC):
    variants_key: str
    default_variants_name: str
    
    model_config = {
        "frozen": True
    }

class YamlQVariantParserSettings(QVariantParserSettings):
    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.YAML

