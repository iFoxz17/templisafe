from abc import ABC
from dataclasses import dataclass, make_dataclass
from typing import Any

from dataclasses import field

from templisafe.provider.source_provider import SourceProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.source import Source
from templisafe.task import TaskBundle

@dataclass(frozen=True, slots=True)
class SourceBundle(ABC):
    """Base class for dynamically generated dataclasses containing resolved `Source` fields."""
    pass

class SourceService:
    """Service responsible for resolving `Source` and `SourceSettings` fields from a `TaskBundle`."""

    __slots__: tuple[str, ...] = ("_source_provider", "_field_selector")

    def __init__(
            self, 
            source_provider: SourceProvider,
            field_selector: FieldSelector
            ) -> None:
        self._source_provider: SourceProvider = source_provider
        self._field_selector: FieldSelector = field_selector 

    def process(self, task_bundle: TaskBundle) -> SourceBundle:
        """
        Extract and resolve all `Source` and `SourceSettings` fields from a `TaskBundle`.

        Parameters
        ----------
        task_bundle : TaskBundle
            The input task containing fields that may include Source or SourceSettings.

        Returns
        -------
        SourceBundle
            A dynamically created dataclass containing only the resolved `Source` fields.
        """

        source_fields: dict[str, Any] = (
            self._field_selector.select_by_type(
                obj=task_bundle, 
                types=(Source, SourceSettings)
                )
        )

        # Dynamically create a dataclass with only resolved fields
        DerivedSourceBundle: type[SourceBundle] = make_dataclass(
            cls_name="SourceBundle",
            fields=[
                (
                    k, 
                    Source, 
                    field(default=self._source_provider.provide(v))
                ) 
                for k, v in source_fields.items()],
            bases=(SourceBundle,),
            frozen=True,
            slots=True,
        )
        return DerivedSourceBundle()