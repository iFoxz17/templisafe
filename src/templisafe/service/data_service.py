from templisafe.content.content import Content
from templisafe.provider.content_provider import ContentGroup, ContentProvider, SourceGroup
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.source.source import Source
from templisafe.task import TaskBundle

class DataService:
    """Service responsible for resolving Content fields from a TaskBundle."""

    __slots__ = ("_content_provider", "_field_selector")

    def __init__(self, content_provider: ContentProvider, field_selector: FieldSelector) -> None:
        self._content_provider: ContentProvider = content_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, source_bundle: TaskBundle) -> TaskBundle:
        """
        Process a TaskBundle with all fields at least at the Source level
        and produce a DataBundle with resolved Content fields.
        """
        # Get source executor settings if present
        source_executor_settings: SourceExecutorSettings | None = source_bundle.source_executor_settings

        # Select all fields that are Source
        source_fields: dict[str, Source] = self._field_selector.select_by_type(
            source_bundle, types=Source
        )

        # Build a SourceGroup from the selected fields
        source_group = SourceGroup(source_fields)

        # Produce Content from the sources
        content_group: ContentGroup = self._content_provider.provide(
            source_group=source_group,
            source_executor=source_executor_settings
        )
        return source_bundle.model_copy(update=content_group.contents)
