from templisafe.content.content import Content, ContentType
from templisafe.parser.config.config_parser import Config, ConfigParser
from templisafe.provider.config_parser_provider import ConfigParserProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.task import TaskBundle

class ConfigService:
    """Service responsible for resolving Config fields from a DataBundle."""

    __slots__: tuple[str, ...] = ("_config_parser_provider", "_field_selector")

    def __init__(self, config_parser_provider: ConfigParserProvider, field_selector: FieldSelector) -> None:
        self._config_parser_provider: ConfigParserProvider = config_parser_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, data_bundle: TaskBundle) -> TaskBundle:
        """
        Process a DataBundle with all fields at least at the Content level
        and produce a ConfigBundle with resolved Config fields.
        """

        # Prepare a parser cache per ContentType
        content_fields: dict[str, Content] = self._field_selector.select_by_type(data_bundle, Content)
        config_fields: dict[str, Config] = {}
        
        for name, content in content_fields.items():
            content_type: ContentType = content.type_
            parser: ConfigParser = self._config_parser_provider.provide(content_type) 
            config: Config = parser.parse(content.payload)
            config_fields[name] = config

        return data_bundle.model_copy(update=config_fields)
