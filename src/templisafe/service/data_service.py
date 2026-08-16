from templisafe.content.content import Content
from templisafe.core.field_selector import FieldSelector
from templisafe.provider.content_provider import (
    ContentGroup,
    ContentProvider,
    SourceGroup,
)
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.source.source import Source
from templisafe.task.task import TaskBundle


class DataService:
    """Service responsible for resolving Content fields from a TaskBundle."""

    __slots__ = ("_content_provider", "_field_selector")

    def __init__(self, content_provider: ContentProvider, field_selector: FieldSelector) -> None:
        self._content_provider: ContentProvider = content_provider
        self._field_selector: FieldSelector = field_selector

    def _collect_sources(self, value, prefix: str, sources: dict[str, Source]) -> None:
        if isinstance(value, Source):
            sources[prefix] = value
            return
        if isinstance(value, list):
            for index, item in enumerate(value):
                self._collect_sources(item, f"{prefix}.{index}", sources)

    def _replace_sources(self, value, prefix: str, contents: dict[str, Content]):
        if isinstance(value, Source):
            return contents[prefix]
        if isinstance(value, list):
            return [self._replace_sources(item, f"{prefix}.{index}", contents) for index, item in enumerate(value)]
        return value

    def process(self, source_bundle: TaskBundle) -> TaskBundle:
        """
        Process a TaskBundle with all fields at least at the Source level
        and produce a DataBundle with resolved Content fields.
        """
        # Get source executor settings if present
        source_executor_settings = source_bundle.source_executor_settings
        if not isinstance(source_executor_settings, SourceExecutorSettings):
            source_executor_settings = None

        # Select all fields that are Source
        source_fields: dict[str, Source] = self._field_selector.select_by_type(source_bundle, types=Source)
        for name in type(source_bundle).model_fields:
            if name not in source_fields:
                self._collect_sources(getattr(source_bundle, name), name, source_fields)

        if not source_fields:
            return source_bundle

        # Build a SourceGroup from the selected fields
        source_group = SourceGroup(source_fields)

        # Produce Content from the sources
        content_group: ContentGroup = self._content_provider.provide(
            source_group=source_group, source_executor=source_executor_settings
        )
        updates = dict(content_group.contents)
        for name in type(source_bundle).model_fields:
            if name not in updates:
                replaced = self._replace_sources(getattr(source_bundle, name), name, content_group.contents)
                if replaced is not getattr(source_bundle, name):
                    updates[name] = replaced

        return source_bundle.model_copy(update=updates)
