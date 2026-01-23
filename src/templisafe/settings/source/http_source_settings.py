from pydantic import Field
from overrides import overrides

from templisafe.settings.source.source_settings import SourceSettings, SourceKind

class HttpSourceSettings(SourceSettings):
    """
    Settings for fetching content from an HTTP endpoint.
    The source `content_type` must be explicitly set.
    """

    url: str = Field(..., description="The URL to fetch content from")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.HTTP

SourceSettings.register_source_kind(SourceKind.HTTP, HttpSourceSettings)
