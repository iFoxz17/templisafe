from abc import ABC
from dataclasses import dataclass, make_dataclass, field, asdict

from templisafe.content.content import Content
from templisafe.provider.content_provider import ContentGroup, ContentProvider, SourceGroup
from templisafe.service.field_selector import FieldSelector
from templisafe.service.source_service import SourceBundle
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.source.source import Source
from templisafe.task import TaskBundle


@dataclass(frozen=True, slots=True)
class DataBundle(ABC):
    """Base class for dynamically generated dataclasses containing resolved `Content` fields."""
    pass


class DataService:
    """Service responsible for resolving data from task and source bundles."""

    __slots__: tuple[str, ...] = ("_content_provider", "_field_selector")

    def __init__(self, content_provider: ContentProvider, field_selector: FieldSelector) -> None:
        self._content_provider: ContentProvider = content_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, task_bundle: TaskBundle, source_bundle: SourceBundle) -> DataBundle:
        """
        Process a `TaskBundle` and a `SourceBundle` to produce a `DataBundle`.

        Parameters
        ----------
        task_bundle : TaskBundle
            The input task containing fields that may include `Source` objects.
        source_bundle : SourceBundle
            A previously resolved `SourceBundle` with additional `Source` objects.

        Returns
        -------
        DataBundle
            A dynamically created dataclass containing only resolved `Content` fields.
        """

        source_executor_settings: SourceExecutorSettings | None = task_bundle.source_executor_settings

        # Extract Source fields from the task bundle
        task_sources: dict[str, Source] = self._field_selector.select_by_type(task_bundle, types=Source)

        # Extract Source fields from the source bundle
        source_sources: dict[str, Source] = asdict(source_bundle)

        # Merge all source fields for the content provider
        merged_sources: dict[str, Source] = task_sources | source_sources
        source_group = SourceGroup(merged_sources)

        # Produce content from the sources
        content_group: ContentGroup = self._content_provider.provide(
            source_group=source_group,
            source_executor=source_executor_settings
            )

        # Dynamically create a DataBundle dataclass with only resolved fields
        DerivedDataBundle: type[DataBundle] = make_dataclass(
            cls_name="DataBundle",
            fields=[(k, Content, field(default=v)) for k, v in content_group.contents],
            bases=(DataBundle,),
            frozen=True,
            slots=True,
        )

        return DerivedDataBundle()