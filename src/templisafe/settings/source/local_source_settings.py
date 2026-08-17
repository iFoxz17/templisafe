from overrides import overrides
from pydantic import Field

from templisafe.settings.source.source_settings import SourceKind, SourceSettings


class LocalSourceSettings(SourceSettings):
    """
    Settings for local filesystem sources.
    The source `content_type` can be inferred from the `path` extension, if present.
    """

    path: str = Field(..., description="The path of the file")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.LOCAL


SourceSettings.register_source_kind(SourceKind.LOCAL, LocalSourceSettings)
