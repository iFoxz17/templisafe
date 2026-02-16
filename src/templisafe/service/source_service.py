from dataclasses import make_dataclass, field, fields
from typing import Any, get_type_hints

from templisafe.provider.source_provider import SourceProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.source import Source
from templisafe.task import TaskBundle


class SourceService:
    """Service responsible for resolving `Source` and `SourceSettings` fields from a `TaskBundle`."""

    __slots__ = ("_source_provider", "_field_selector")

    def __init__(self, source_provider: SourceProvider, field_selector: FieldSelector) -> None:
        self._source_provider: SourceProvider = source_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, task_bundle: TaskBundle) -> TaskBundle:
        """
        Extract and resolve all `Source` and `SourceSettings` fields from a `TaskBundle`
        and return a dynamically narrowed dataclass with resolved fields.
        """
        # Select fields that need resolution
        source_fields: dict[str, Source | SourceSettings] = self._field_selector.select_by_type(
            obj=task_bundle,
            types=(Source, SourceSettings)
        )

        provider: SourceProvider = self._source_provider
        type_hints: dict[str, Any] = get_type_hints(type(task_bundle))

        # Dynamically create field definitions for the new dataclass
        fs: list[tuple[str, type, Any]] = []
        for f in fields(task_bundle):
            if f.name in source_fields:
                # Narrow type to Source
                fs.append((f.name, Source, field(default=provider.provide(getattr(task_bundle, f.name)))))
            else:
                # Keep original type and value
                field_type: type = type_hints.get(f.name, f.type)
                fs.append((f.name, field_type, field(default=getattr(task_bundle, f.name))))

        # Create the narrowed dataclass
        SourceBundle: type[TaskBundle] = make_dataclass(
            cls_name="SourceBundle",
            fields=fs,
            bases=(type(task_bundle),),
            frozen=True,
            slots=True,
            kw_only=True,
        )

        # Instantiate the new dataclass
        return SourceBundle()