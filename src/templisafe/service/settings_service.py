from dataclasses import make_dataclass, field, fields
from typing import Any, get_type_hints

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

        # Get type hints from the input bundle for any non-Content fields
        type_hints: dict[str, Any] = get_type_hints(type(data_bundle))

        # Dynamically create the SettingsBundle dataclass
        fs: list[tuple[str, type, Any]] = []
        for f in fields(data_bundle):
            if f.name in settings_fields:
                # Use a default parameter to capture the current value of settings_fields[f.name]
                # This avoids the common “late binding” problem in Python loops, ensuring each
                # field’s default_factory returns the correct Settings at dataclass instantiation.
                fs.append((f.name, object, field(default_factory=lambda c=settings_fields[f.name]: c)))
            else:
                # Keep original type and value (pass-through)
                field_type: type = type_hints.get(f.name, f.type)
                fs.append((f.name, field_type, field(default=getattr(data_bundle, f.name))))

        SettingsBundle: type[TaskBundle] = make_dataclass(
            cls_name="SettingsBundle",
            fields=fs,
            bases=(type(data_bundle),),
            frozen=True,
            slots=True,
            kw_only=True,
        )

        return SettingsBundle()