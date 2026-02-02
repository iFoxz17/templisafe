from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

class HttpAsyncSessionSettings(Settings):
    """Configuration for the shared asynchronous HTTP session."""

    max_connections: int = Field(
        default=100,
        description=(
            "Maximum total number of simultaneous open connections. "
            "Set to 0 to disable the limit (unbounded). "
        ),
        ge=0,
    )

    max_connections_per_host: int = Field(
        default=100,
        description=(
            "Maximum number of simultaneous open connections per host. "
            "Set to 0 to disable the limit (unbounded). "
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
            "Time-to-live for cached DNS entries in seconds. "
            "A higher value reduces DNS lookups under high concurrency."
        ),
        ge=0,
    )

Settings.register_kind(SettingsKind.HTTP_ASYNC_SESSION_SETTINGS, HttpAsyncSessionSettings)