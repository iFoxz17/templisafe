from abc import ABC
from typing import Type, TypeVar, Any, cast, ClassVar
from pydantic import BaseModel, ConfigDict, ValidationError
from enum import Enum

from templisafe.exceptions.settings_error import SettingsError
from templisafe.exceptions.load_error import LoadError
from templisafe.loader.loader import *

class SettingsKind(str, Enum):
    MANAGER_SETTINGS = "manager_settings"
    TEMPLATE_PARSER_SETTINGS = "template_parser_settings" 
    SCHEMA_PARSER_SETTINGS = "schema_parser_settings"
    VARIANT_PARSER_SETTINGS = "variant_parser_settings"
    SOURCE_EXECUTOR_SETTINGS = "source_loader_settings"
    COMPILER_SETTINGS = "compiler_settings"
    RENDERER_SETTINGS = "renderer_settings"
    
T = TypeVar("T", bound="Settings")

class Settings(BaseModel, ABC):
    """Abstract base class for all settings with centralized loading."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )

    # -----------------------------
    # Factory for polymorphic creation
    # -----------------------------
    _KIND_MAP: ClassVar[dict[SettingsKind, Type["Settings"]]] = {}

    @classmethod
    def register_kind(cls, kind: SettingsKind, klass: Type["Settings"]) -> None:
        cls._KIND_MAP[kind] = klass

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """Factory to create Settings instances."""

        target_cls: Type[T] = cls
        if "kind" in kwargs:
            kind: Any = kwargs.pop("kind")
            if isinstance(kind, str):
                try:
                    kind = SettingsKind(kind.lower())
                except ValueError:
                    raise ValueError(f"Invalid settings kind: {kind!r}")

                if not isinstance(kind, SettingsKind):
                    raise ValueError(f"Invalid settings kind: {kind!r}")
                
                maybe_target_cls: type | None = cls._KIND_MAP.get(kind)
                if maybe_target_cls is None:
                    raise ValueError(f"Unknown settings kind: {kind!r}")
                target_cls = maybe_target_cls
        try:
            return cast(T, target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {cls.__name__}: {e}") from e

    @classmethod
    def _parse_config(cls: Type[T], config: dict[str, Any]) -> T:
        if not isinstance(config, dict):
            raise ValueError(f"Expected a dict, got {type(config).__name__}")
        return cls.create(**config)

    @classmethod
    def _load_yaml(cls, config_str: str) -> dict[str, Any]:
        try:
            return YamlLoader().load(config_str)    
        except LoadError as e:
            raise SettingsError("Cannot parse YAML configuration") from e
        
    @classmethod
    def _load_json(cls, config_str: str) -> dict[str, Any]:
        try:
            return JsonLoader().load(config_str)    
        except LoadError as e:
            raise SettingsError("Cannot parse JSON configuration") from e
        
    @classmethod
    def _load_toml(cls, config_str: str) -> dict[str, Any]:
        try:
            return TomlLoader().load(config_str)    
        except LoadError as e:
            raise SettingsError("Cannot parse TOML configuration") from e
        
    @classmethod
    def _load_xml(cls, config_str: str) -> dict[str, Any]:
        try:
            return XmlLoader().load(config_str)    
        except LoadError as e:
            raise SettingsError("Cannot parse XML configuration") from e
    
    @classmethod
    def from_yaml(cls: Type[T], config_str: str) -> T:
        """Load settings from a YAML string."""
        return cls._parse_config(cls._load_yaml(config_str))

    @classmethod
    def from_json(cls: Type[T], config_str: str) -> T:
        """Load settings from a JSON string."""
        return cls._parse_config(cls._load_json(config_str))
    
    @classmethod
    def from_toml(cls: Type[T], config_str: str) -> T:
        """Load settings from a TOML string."""
        return cls._parse_config(cls._load_toml(config_str))
    
    @classmethod
    def from_xml(cls: Type[T], config_str: str) -> T:
        """Load settings from a XML string."""
        return cls._parse_config(cls._load_xml(config_str))

    @classmethod
    def from_dict(cls: Type[T], config: dict[str, Any]) -> T:
        """Load settings directly from a dictionary."""
        if not isinstance(config, dict):
            raise SettingsError("Provided config must be a dictionary")
        return cls._parse_config(config)
