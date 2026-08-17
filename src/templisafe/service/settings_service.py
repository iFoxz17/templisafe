from typing import Any

from templisafe.core.field_selector import FieldSelector
from templisafe.exceptions.settings_error import SettingsError
from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.provider.settings_parser_provider import SettingsParserProvider
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.settings import Settings, SettingsKind
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.task.task import TaskBundle

_FIELD_SETTINGS_TYPES: dict[str, tuple[type[Settings], SettingsKind]] = {
    "source_executor_settings": (SourceExecutorSettings, SettingsKind.SOURCE_EXECUTOR_SETTINGS),
    "template_engine": (TemplateEngineSettings, SettingsKind.TEMPLATE_ENGINE_SETTINGS),
    "template_parser_settings": (TemplateParserSettings, SettingsKind.TEMPLATE_PARSER_SETTINGS),
    "schema_parser_settings": (SchemaParserSettings, SettingsKind.SCHEMA_PARSER_SETTINGS),
    "variant_parser_settings": (VariantParserSettings, SettingsKind.VARIANT_PARSER_SETTINGS),
    "compiler_settings": (CompilerSettings, SettingsKind.COMPILER_SETTINGS),
    "renderer_settings": (RendererSettings, SettingsKind.RENDERER_SETTINGS),
}


class SettingsService:
    """Service responsible for resolving Settings fields from a `ConfigBundle`."""

    __slots__: tuple[str, ...] = ("_settings_parser_provider", "_field_selector", "_resource_provider")

    def __init__(
        self,
        settings_parser_provider: SettingsParserProvider,
        field_selector: FieldSelector,
        resource_provider: ResourceProvider,
    ) -> None:
        self._settings_parser_provider: SettingsParserProvider = settings_parser_provider
        self._field_selector: FieldSelector = field_selector
        self._resource_provider: ResourceProvider = resource_provider

    def _settings_kind_for(self, value: dict[str, Any], default_kind: SettingsKind) -> SettingsKind:
        if "kind" not in value:
            return default_kind
        try:
            return SettingsKind(str(value["kind"]).lower())
        except ValueError as exc:
            raise SettingsError(f"Invalid settings kind: {value['kind']!r}") from exc

    def process(self, data_bundle: TaskBundle) -> TaskBundle:
        """
        Process a `ConfigBundle` with all fields at least at the Content level
        and produce a `SettingsBundle` with resolved Settings fields.
        """

        settings_fields: dict[str, Settings] = {}

        for name, value in data_bundle.components.items():
            field_settings = _FIELD_SETTINGS_TYPES.get(name)
            if field_settings is None or value is None or isinstance(value, Settings):
                continue
            if isinstance(value, dict):
                expected_type, default_kind = field_settings
                settings_kind = self._settings_kind_for(value, default_kind)
                settings_config = value if "kind" in value else {"kind": default_kind.value, **value}
                parser: SettingsParser = self._settings_parser_provider.provide(settings_kind)
                settings = self._resource_provider.provide_settings(settings_config, parser)
                if not isinstance(settings, expected_type):
                    raise TypeError(f"Expected {expected_type.__name__} for field '{name}'")
                settings_fields[name] = settings

        return data_bundle.model_copy(update=settings_fields)
