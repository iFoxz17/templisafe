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
    
class XmlLoader(Loader):
    """
    XML configuration loader.
    """

    @overrides
    def load(self, raw: str) -> dict[str, Any]:
        try:
            import xml.etree.ElementTree as ET
        except ModuleNotFoundError as e:
            raise LoadError(
                "XML support requires the standard library 'xml.etree.ElementTree'"
            ) from e

        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            raise LoadError(f"Failed to parse XML configuration: {e}") from e

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
            raise LoadError(f"Failed to convert XML to dict: {e}") from e

        return self._finalize_import(
            config,
            f"XML configuration must have a valid root element, got {type(config).__name__}"
        )


__all__ = [
    "Loader",
    "YamlLoader",
    "JsonLoader",
    "TomlLoader",
    "XmlLoader",
]
