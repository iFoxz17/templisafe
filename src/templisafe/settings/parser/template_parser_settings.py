from overrides import overrides

from templisafe.settings.parser.parser_settings import ParserSettings
from templisafe.util.util import ContentType

class TemplateParserSettings(ParserSettings):

    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.TEXT