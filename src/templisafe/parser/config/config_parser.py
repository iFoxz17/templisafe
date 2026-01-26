"""
Loaders for structured configuration formats (YAML, JSON, TOML, XML).
"""

from abc import ABC, abstractmethod
from typing import Any, Union
from overrides import overrides

from templisafe.exceptions.config_error import ConfigError

Config = Union[dict[str, Any], list[Any]]

class ConfigParser(ABC):
    """Abstract base class for configuration parsers."""

    __slots__: tuple[str, ...] = ()

    @abstractmethod
    def parse(self, payload: str) -> Config:
        """
        Parse a raw string into a `Config`.

        Parameters
        ----------
        payload : str
            The Raw configuration string

        Returns
        -------
        Config
            The parsed configuration.

        Raises
        ------
        ConfigError
            If configuration parsing fails or the result is invalid.
        """
        pass
    
    def _finalize_import(self, config: Any, err_msg: str) -> Config:
        if not isinstance(config, (dict, list)):
            raise ConfigError(err_msg)
        return config


class YamlParser(ConfigParser):
    """YAML configuration parser."""

    @overrides
    def parse(self, payload: str) -> Config:
        import yaml

        try:
            config: Any = yaml.safe_load(payload)
        except yaml.YAMLError as e:
            raise ConfigError(
                f"Failed to parse YAML configuration: {e}"
            ) from e

        return self._finalize_import(
            config,
            f"YAML configuration must be a list or a mapping, got {type(config).__name__}"
            )


class JsonParser(ConfigParser):
    """JSON configuration parser."""

    @overrides
    def parse(self, payload: str) -> Config:
        import json

        try:
            config: Any = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ConfigError(
                "Failed to parse JSON configuration "
                f"(line {e.lineno}, column {e.colno}): {e.msg}"
            ) from e

        return self._finalize_import(
            config,
            f"JSON configuration must be a list or an object, got {type(config).__name__}"
            )


class TomlParser(ConfigParser):
    """TOML configuration parser."""

    @overrides
    def parse(self, payload: str) -> Config:
        try:
            import tomllib                      # Python 3.11+
        except ModuleNotFoundError:
            try:
                import tomli as tomllib         # type: ignore[import-not-found]
            except ModuleNotFoundError as e:
                raise ConfigError(
                    "TOML support requires Python >= 3.11 or the 'tomli' package installed"
                ) from e

        try:
            config: Any = tomllib.loads(payload)
        except Exception as e:
            raise ConfigError(
                f"Failed to parse TOML configuration: {e}"
            ) from e
        
        return self._finalize_import(
            config,
            f"TOML configuration must be a table, got {type(config).__name__}"
            )
    

class XmlParser(ConfigParser):
    """XML configuration parser."""

    @overrides
    def parse(self, payload: str) -> Config:
        try:
            import xml.etree.ElementTree as ET
        except ModuleNotFoundError as e:
            raise ConfigError(
                "XML support requires the standard library 'xml.etree.ElementTree'"
            ) from e

        try:
            root = ET.fromstring(payload)
        except ET.ParseError as e:
            raise ConfigError(f"Failed to parse XML configuration: {e}") from e

        def _element_to_dict(element: ET.Element) -> dict[str, Any]:
            data: dict[str, Any] = {}
            for child in element:
                child_data = _element_to_dict(child)
                tag = child.tag
                if tag in data:
                    if not isinstance(data[tag], list):
                        data[tag] = [data[tag]]
                    data[tag].append(child_data[tag])
                else:
                    data.update(child_data)
            if not data and element.text and element.text.strip():
                return {element.tag: element.text.strip()}
            return {element.tag: data}

        try:
            config = _element_to_dict(root)
        except Exception as e:
            raise ConfigError(f"Failed to convert XML to dict: {e}") from e

        return self._finalize_import(
            config,
            f"XML configuration must have a valid root element, got {type(config).__name__}"
        )


__all__ = [
    "Config",
    "ConfigParser",
    "YamlParser",
    "JsonParser",
    "TomlParser",
    "XmlParser",
]
