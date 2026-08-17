from abc import ABC

from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

##############################################################################################
# Base settings for both sync and async
##############################################################################################


class HttpSessionSettings(Settings, ABC):
    """Common configuration for the shared synchronous HTTP session pool."""

    max_slots: int | None = Field(
        default=None,
        description=(
            "Maximum number of session objects allowed in the pool. If None, the pool can grow without limit."
        ),
        ge=1,
    )

    max_concurrency: int | None = Field(
        default=None,
        description=(
            "Maximum number of concurrent requests allowed globally across all sessions. "
            "If None, no global concurrency limit is enforced."
        ),
        ge=1,
    )


##############################################################################################
# Sync settings
##############################################################################################


class HttpSyncSessionSettings(HttpSessionSettings):
    """Configuration for the shared synchronous HTTP session pool."""

    pool_connections: int = Field(
        default=10,
        description=("Maximum number of connection pools to cache (see requests.adapters.HTTPAdapter)."),
        ge=1,
    )

    pool_maxsize: int = Field(
        default=10,
        description=(
            "Maximum number of connections to save in each connection pool (see requests.adapters.HTTPAdapter)."
        ),
        ge=1,
    )


Settings.register_kind(SettingsKind.HTTP_SYNC_SESSION_SETTINGS, HttpSyncSessionSettings)

##############################################################################################
# Async settings
##############################################################################################


class HttpAsyncSessionSettings(HttpSessionSettings):
    """Configuration for the shared asynchronous HTTP session."""

    max_connections: int = Field(
        default=1000,
        description=(
            "Maximum total number of simultaneous open connections. Set to 0 to disable the limit (unbounded). "
        ),
        ge=0,
    )

    max_connections_per_host: int = Field(
        default=1000,
        description=(
            "Maximum number of simultaneous open connections per host. Set to 0 to disable the limit (unbounded). "
        ),
        ge=0,
    )

    force_close: bool = Field(
        default=False,
        description=(
            "Whether to force-close connections after each request instead "
            "of reusing them. Disabling connection reuse significantly "
            "reduces performance and should generally remain False."
        ),
    )

    ttl_dns_cache: int | None = Field(
        default=None,
        description=(
            "Time-to-live for cached DNS entries in seconds. A higher value reduces DNS lookups under high concurrency."
        ),
        ge=0,
    )


Settings.register_kind(SettingsKind.HTTP_ASYNC_SESSION_SETTINGS, HttpAsyncSessionSettings)
