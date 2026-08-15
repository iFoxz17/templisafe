from templisafe.core.task import TaskBundle
from templisafe.provider.source_provider import SourceProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.source import Source


class SourceService:
    """Service responsible for resolving `Source` and `SourceSettings` fields from a `TaskBundle`."""

    __slots__ = ("_source_provider", "_field_selector")

    def __init__(self, source_provider: SourceProvider, field_selector: FieldSelector) -> None:
        self._source_provider: SourceProvider = source_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, task_bundle: TaskBundle) -> TaskBundle:
        """
        Extract and resolve all `Source` and `SourceSettings` fields from a `TaskBundle`
        and return the bundle with those fields resolved to `Source` instances.
        """
        source_fields: dict[str, Source | SourceSettings] = self._field_selector.select_by_type(
            obj=task_bundle, types=(Source, SourceSettings)
        )
        resolved = {name: self._source_provider.provide(value) for name, value in source_fields.items()}
        return task_bundle.model_copy(update=resolved)
