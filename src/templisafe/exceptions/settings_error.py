from typing import Any

class SettingsError(Exception):
    """Base class for settings-related exceptions."""
    pass

class UnsupportedSettingsError(SettingsError):
    """Raised when trying to parse a settings of an unsupported settings kind."""

    def __init__(self, settings_kind: Any) -> None:
        self.settings_kind: Any = settings_kind
        super().__init__(
            f"Unsupported settings kind: {settings_kind!r}"
        )

class SettingsConfigError(SettingsError):
    """Raised when trying to create a `Settings` from an unallowed `Config`."""

    def __init__(self, config: Any) -> None:
        self.config: Any = config
        super().__init__(
            f"Cannot create a settings instance from the configuration type: {config!r}"
        )