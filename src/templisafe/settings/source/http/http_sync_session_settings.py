from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

class HttpSyncSessionSettings(Settings):
    """Configuration for the shared synchronous HTTP session pool."""

    pool_connections: int = Field(
        default=10,
        description=(
            "Maximum number of connection pools to cache (see requests.adapters.HTTPAdapter)."
        ),
        ge=1,
    )

    pool_maxsize: int = Field(
        default=10,
        description=(
            "Maximum number of connections to save in each connection pool (see requests.adapters.HTTPAdapter)."
        ),
        ge=1,
    )

    max_slots: int | None = Field(
        default=20,
        description=(
            "Maximum number of session objects allowed in the pool. "
            "If None, the pool can grow without limit."
        ),
        ge=1,
    )

    max_concurrency: int | None = Field(
        default=100,
        description=(
            "Maximum number of concurrent requests allowed globally across all sessions. "
            "If None, no global concurrency limit is enforced."
        ),
        ge=1,
    )

# Register the settings kind
Settings.register_kind(SettingsKind.HTTP_SYNC_SESSION_SETTINGS, HttpSyncSessionSettings)
