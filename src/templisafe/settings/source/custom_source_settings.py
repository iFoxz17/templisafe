from typing import Any

from overrides import overrides
from pydantic import Field

from templisafe.settings.source.source_settings import SourceKind, SourceSettings


class CustomSourceSettings(SourceSettings):
    """
    Settings for defining custom source objects.
    The source `content_type` must be explicitly set.
    """

    context: Any = Field(None, description="The context to use inside the custom source object")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.CUSTOM


SourceSettings.register_source_kind(SourceKind.CUSTOM, CustomSourceSettings)
