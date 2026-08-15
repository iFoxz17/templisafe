from typing import Any

from templisafe.exceptions.settings_error import SettingsConfigError
from templisafe.parser.config.config_parser import Config
from templisafe.settings.settings import Settings
from templisafe.settings.source.source_settings import SourceSettings


class SettingsParser:
    """Parser for base settings."""

    __slots__: tuple[str, ...] = ()

    def _validate_config(self, config: Any) -> dict[str, Any]:
        if not isinstance(config, dict):
            raise SettingsConfigError(config)
        return config

    def parse(self, config: Config) -> Settings:
        """
        Parse a configuration into a `Settings`.

        Parameters
        ----------
        config: Config
            The settings configuration. Must be a dict

        Returns
        -------
        Settings
            The parsed settings.

        Raises
        ------
        SettingsError
            If settings parsing fails or the result is invalid.
        """
        config_validated: dict[str, Any] = self._validate_config(config)
        return Settings.from_dict(config_validated)


class SourceSettingsParser(SettingsParser):
    """Parser for `SourceSettings` objects."""

    def parse(self, config: Config) -> Settings:
        config_validated: dict[str, Any] = self._validate_config(config)
        return SourceSettings.from_dict(config_validated)


__all__ = [
    "Config",
    "SettingsParser",
    "SourceSettingsParser",
]
