from templisafe.content.content import Content, ContentType
from templisafe.core.field_selector import FieldSelector
from templisafe.parser.config.config_parser import Config, ConfigParser
from templisafe.provider.config_parser_provider import ConfigParserProvider
from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.task.task import TaskBundle


class ConfigService:
    """Service responsible for resolving Config fields from a DataBundle."""

    __slots__: tuple[str, ...] = ("_config_parser_provider", "_field_selector", "_resource_provider")

    def __init__(
        self,
        config_parser_provider: ConfigParserProvider,
        field_selector: FieldSelector,
        resource_provider: ResourceProvider,
    ) -> None:
        self._config_parser_provider: ConfigParserProvider = config_parser_provider
        self._field_selector: FieldSelector = field_selector
        self._resource_provider: ResourceProvider = resource_provider

    def _parse_content(self, content: Content) -> Config | Content:
        if content.type_ is ContentType.TEXT:
            return content
        parser: ConfigParser = self._config_parser_provider.provide(content.type_)
        return self._resource_provider.provide_config(content.payload, parser)

    def _parse_value(self, value):
        if isinstance(value, Content):
            return self._parse_content(value)
        if isinstance(value, list):
            return [self._parse_value(item) for item in value]
        return value

    def process(self, data_bundle: TaskBundle) -> TaskBundle:
        """
        Process a DataBundle with all fields at least at the Content level
        and produce a ConfigBundle with resolved Config fields.
        """

        # Prepare a parser cache per ContentType
        content_fields: dict[str, Content] = self._field_selector.select_by_type(data_bundle, Content)
        config_fields: dict[str, Config] = {}

        for name, content in content_fields.items():
            parsed = self._parse_content(content)
            if not isinstance(parsed, Content):
                config_fields[name] = parsed

        for name in type(data_bundle).model_fields:
            if name not in config_fields:
                parsed = self._parse_value(getattr(data_bundle, name))
                if parsed is not getattr(data_bundle, name):
                    config_fields[name] = parsed

        return data_bundle.model_copy(update=config_fields)
