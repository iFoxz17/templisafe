from overrides import overrides
from pydantic import Field

from templisafe.settings.source.source_settings import SourceKind, SourceSettings


class InlineSourceSettings(SourceSettings):
    """
    Settings for inline content sources.
    The source `content_type` must be explicitly set.
    """

    content: str = Field(..., description="The inline content")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.INLINE


SourceSettings.register_source_kind(SourceKind.INLINE, InlineSourceSettings)
