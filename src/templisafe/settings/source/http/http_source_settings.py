from overrides import overrides
from pydantic import Field

from templisafe.settings.source.source_settings import SourceKind, SourceSettings

from .http_session_settings import HttpAsyncSessionSettings, HttpSyncSessionSettings


class HttpSourceSettings(SourceSettings):
    """
    Settings for fetching content from an HTTP endpoint.
    The source `content_type` must be explicitly set.
    """

    url: str = Field(..., description="The URL to fetch content from")

    timeout: float = Field(
        default=30,
        description=(
            "Total request timeout in seconds. Applies to the entire request "
            "lifecycle including connection, redirects and response reading."
        ),
        gt=0,
    )

    sync_session_settings: HttpSyncSessionSettings = Field(
        default_factory=HttpSyncSessionSettings,
        description="The http session settings to use for the synchronous flow",
    )

    async_session_settings: HttpAsyncSessionSettings = Field(
        default_factory=HttpAsyncSessionSettings,
        description="The http session settings to use for the asynchronous flow",
    )

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.HTTP


SourceSettings.register_source_kind(SourceKind.HTTP, HttpSourceSettings)
