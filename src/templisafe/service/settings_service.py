from templisafe.content.content import Content, ContentType
from templisafe.parser.settings.settings_parser import Settings, SettingsParser
from templisafe.provider.settings_parser_provider import SettingsParserProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.task import TaskBundle

class SettingsService:
    """Service responsible for resolving Settings fields from a `ConfigBundle`."""

    __slots__: tuple[str, ...] = ("_settings_parser_provider", "_field_selector")

    def __init__(self, settings_parser_provider: SettingsParserProvider, field_selector: FieldSelector) -> None:
        self._settings_parser_provider: SettingsParserProvider = settings_parser_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, data_bundle: TaskBundle) -> TaskBundle:
        """
        Process a `ConfigBundle` with all fields at least at the Content level
        and produce a `SettingsBundle` with resolved Settings fields.
        """

        # Prepare a parser cache per ContentType
        content_fields: dict[str, Content] = self._field_selector.select_by_type(data_bundle, Content)
        settings_fields: dict[str, Settings] = {}
        
        for name, content in content_fields.items():
            content_type: ContentType = content.type_
            parser: SettingsParser = self._settings_parser_provider.provide(content_type) 
            settings_fields[name] = parser.parse(content.payload)

        return data_bundle.model_copy(update=settings_fields)
