from typing import Any

from templisafe.core.task import TaskBundle
from templisafe.provider.settings_parser_provider import SettingsParserProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.settings import Settings


class SettingsService:
    """Service responsible for resolving Settings fields from a `ConfigBundle`."""

    __slots__: tuple[str, ...] = ("_settings_parser_provider", "_field_selector")

    def __init__(
        self,
        settings_parser_provider: SettingsParserProvider,
        field_selector: FieldSelector,
    ) -> None:
        self._settings_parser_provider: SettingsParserProvider = settings_parser_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, data_bundle: TaskBundle) -> TaskBundle:
        """
        Process a `ConfigBundle` with all fields at least at the Content level
        and produce a `SettingsBundle` with resolved Settings fields.
        """

        config_fields: dict[str, dict[str, Any]] = self._field_selector.select_by_type(data_bundle, dict)
        settings_fields: dict[str, Settings] = {}

        for name, config in config_fields.items():
            settings_fields[name] = Settings.from_dict(config)

        return data_bundle.model_copy(update=settings_fields)
