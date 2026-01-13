"""
Loaders for structured configuration formats (YAML, JSON, TOML).
"""

from abc import ABC, abstractmethod
from typing import Any
from overrides import overrides

from templisafe.exceptions.load_error import LoadError

class Loader(ABC):
    """
    Abstract base class for configuration loaders.
    """

    __slots__: tuple[str, ...] = ()

    @abstractmethod
    def load(self, raw: str) -> dict[str, Any]:
        """
        Parse a raw string into a configuration dictionary.

        :param raw: Raw configuration string
        :raises LoadError: If parsing fails or the result is invalid
        """
        raise NotImplementedError
    
    def _finalize_import(self, config: Any, err_msg: str) -> dict[str, Any]:
        if not isinstance(config, dict):
            raise LoadError(err_msg)
        return config

class YamlLoader(Loader):
    """
    YAML configuration loader.
    """

    @overrides
    def load(self, raw: str) -> dict[str, Any]:
        import yaml

        try:
            config: Any = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            raise LoadError(
                f"Failed to load YAML configuration: {e}"
            ) from e

        return self._finalize_import(
            config,
            "YAML configuration must be a mapping, got {type(config).__name__}"
            )


class JsonLoader(Loader):
    """
    JSON configuration loader.
    """

    @overrides
    def load(self, raw: str) -> dict[str, Any]:
        import json

        try:
            config: Any = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LoadError(
                "Failed to load JSON configuration "
                f"(line {e.lineno}, column {e.colno}): {e.msg}"
            ) from e

        return self._finalize_import(
            config,
            f"JSON configuration must be an object, got {type(config).__name__}"
            )


class TomlLoader(Loader):
    """
    TOML configuration loader.
    """

    @overrides
    def load(self, raw: str) -> dict[str, Any]:
        try:
            import tomllib                      # Python 3.11+
        except ModuleNotFoundError:
            try:
                import tomli as tomllib         # type: ignore[import-not-found]
            except ModuleNotFoundError as e:
                raise LoadError(
                    "TOML support requires Python >= 3.11 or the 'tomli' package installed"
                ) from e

        try:
            config: Any = tomllib.loads(raw)
        except Exception as e:
            raise LoadError(
                f"Failed to load TOML configuration: {e}"
            ) from e
        
        return self._finalize_import(
            config,
            f"TOML configuration must be a table, got {type(config).__name__}"
            )


__all__ = [
    "Loader",
    "YamlLoader",
    "JsonLoader",
    "TomlLoader",
]
