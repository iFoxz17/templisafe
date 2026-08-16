from templisafe.core.field_selector import FieldSelector
from templisafe.provider.source_provider import SourceProvider
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.source import Source
from templisafe.task.task import TaskBundle


class SourceService:
    """Service responsible for resolving `Source` and `SourceSettings` fields from a `TaskBundle`."""

    __slots__ = ("_source_provider", "_field_selector")

    def __init__(self, source_provider: SourceProvider, field_selector: FieldSelector) -> None:
        self._source_provider: SourceProvider = source_provider
        self._field_selector: FieldSelector = field_selector

    def _resolve_value(self, value):
        if isinstance(value, (Source, SourceSettings)):
            return self._source_provider.provide(value)
        if isinstance(value, list):
            return [self._resolve_value(item) for item in value]
        return value

    def process(self, task_bundle: TaskBundle) -> TaskBundle:
        """
        Extract and resolve all `Source` and `SourceSettings` fields from a `TaskBundle`
        and return the bundle with those fields resolved to `Source` instances.
        """
        source_fields: dict[str, Source | SourceSettings] = self._field_selector.select_by_type(
            obj=task_bundle, types=(Source, SourceSettings)
        )
        resolved = {name: self._source_provider.provide(value) for name, value in source_fields.items()}

        for name in type(task_bundle).model_fields:
            if name not in resolved:
                resolved_value = self._resolve_value(getattr(task_bundle, name))
                if resolved_value is not getattr(task_bundle, name):
                    resolved[name] = resolved_value

        return task_bundle.model_copy(update=resolved)
