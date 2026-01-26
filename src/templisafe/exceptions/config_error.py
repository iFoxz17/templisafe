from typing import Any
from templisafe.content.content import ContentType

class ConfigError(Exception):
    """Base class for config-related exceptions."""
    pass

class UnsopportedConfigError(ConfigError):
    """Raised when trying to parse a configuration of an unsupported content type."""

    def __init__(self, content_type: ContentType) -> None:
        self.content_type: ContentType = content_type
        super().__init__(
            f"Unsupported configuration content type: {content_type!r}"
        )

class SettingsConfigError(ConfigError):
    """Raised when trying to create a `Settings` from an unallowed `Config`."""

    def __init__(self, config: Any) -> None:
        self.config: Any = config
        super().__init__(
            f"Cannot create a settings instance from the configuration type: {config!r}"
        )
