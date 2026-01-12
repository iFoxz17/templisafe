from abc import ABC, abstractmethod
from typing import Type, TypeVar, Any, Dict
from pydantic import BaseModel, ConfigDict
import json
import yaml

from templisafe.exceptions.settings_error import SettingsError

T = TypeVar("T", bound="Settings")

class Settings(BaseModel, ABC):
    """Abstract base class for all settings with centralized loading."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )

    @classmethod
    @abstractmethod
    def _parse_config(cls: Type[T], config: Dict[str, Any]) -> T:
        """Convert a parsed config dict into a concrete Settings instance."""
        pass

    @classmethod
    def _load_yaml(cls, config_str: str) -> dict[str, Any]:
        """Load settings from a YAML string."""
        try:
            config: Dict[str, Any] = yaml.safe_load(config_str)
            if not isinstance(config, dict):
                raise SettingsError("Parsed YAML is not a dictionary")
        except yaml.YAMLError as e:
            raise SettingsError("Cannot parse YAML configuration") from e
        return config
    
    @classmethod
    def _load_json(cls, config_str: str) -> dict[str, Any]:
        """Load settings from a JSON string."""
        try:
            config: Dict[str, Any] = json.loads(config_str)
            if not isinstance(config, dict):
                raise SettingsError("Parsed JSON is not a dictionary")
        except (json.JSONDecodeError, TypeError) as e:
            raise SettingsError("Cannot parse JSON configuration") from e
        return config
    
    @classmethod
    def from_yaml(cls: Type[T], config_str: str) -> T:
        """Load settings from a YAML string."""
        return cls._parse_config(cls._load_yaml(config_str))

    @classmethod
    def from_json(cls: Type[T], config_str: str) -> T:
        """Load settings from a JSON string."""
        return cls._parse_config(cls._load_json(config_str))

    @classmethod
    def from_dict(cls: Type[T], config: Dict[str, Any]) -> T:
        """Load settings directly from a dictionary."""
        if not isinstance(config, dict):
            raise SettingsError("Provided config must be a dictionary")
        return cls._parse_config(config)
