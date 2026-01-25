from typing import Any, TypeVar, cast
from pydantic import ValidationError, Field
from enum import Enum
from overrides import overrides

from templisafe.config.config_loader import Config
from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="TemplateEngineSettings")

class TemplateEngineKind(str, Enum):
    JINJA = "jinja"
    DJANGO = "django"
    CUSTOM = "custom"

class TemplateEngineSettings(Settings):
    """Settings class for defining template engines."""

    engine_kind: TemplateEngineKind = Field(..., description="The template engine kind")
    config: dict[str, Any] = Field({}, description="The configurations of the engine")

    @classmethod
    def _prepare_kwargs(cls: type[T], kwargs: dict[str, Any]) -> dict[str, Any]:
        engine_kind: Any = kwargs.pop("engine_kind", None)
        if engine_kind is None:
            raise ValueError("Missing 'engine_kind' field to determine engine type")

        if isinstance(engine_kind, str):
            try:
                engine_kind = TemplateEngineKind(engine_kind.lower())
            except ValueError:
                raise ValueError(f"Invalid kind: {engine_kind!r}")
        kwargs["engine_kind"] = engine_kind

        # Check for multiple config sources
        config_sources = ["config", "config_yaml", "config_json"]
        provided = [key for key in config_sources if key in kwargs]
        if len(provided) > 1:
            raise ValueError(
                f"Multiple configuration sources provided: {provided}. "
                "Please provide only one of 'config', 'config_yaml' or 'config_json'."
            )

        # Normalize 'config' to a dict
        cfg: dict[str, Any] = {}
        if "config" in kwargs:
            maybe_cfg: Any = kwargs.pop("config")
            if not isinstance(maybe_cfg, dict):
                raise ValueError(f"Expected 'config' to be a dict, got {type(maybe_cfg).__name__}")
            cfg = maybe_cfg
        elif "config_yaml" in kwargs:
            cfg_yaml: Any = kwargs.pop("config_yaml")
            if not isinstance(cfg_yaml, str):
                raise ValueError(f"Expected 'config_yaml' to be a str, got {type(cfg_yaml).__name__}")
            cfg = cls._load_yaml(cfg_yaml)
        elif "config_json" in kwargs:
            cfg_json: Any = kwargs.pop("config_json")
            if not isinstance(cfg_json, str):
                raise ValueError(f"Expected 'config_json' to be a str, got {type(cfg_json).__name__}")
            cfg = cls._load_json(cfg_json)

        kwargs["config"] = cfg
        return {"kwargs": kwargs}

    @classmethod
    @overrides
    def _parse_config(cls: type[T], config: Config) -> T:
        prepared: dict[str, Any] = cls._prepare_kwargs(cls._validate_config(config))
        kwargs: dict[str, Any] = prepared["kwargs"]

        try:
            return cast(T, cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {cls.__name__}: {e}") from e

    @classmethod
    @overrides
    def create(cls: type[T], **kwargs) -> T:
        """Factory method to create a TemplateEngineSettings instance."""
        prepared: dict[str, Any] = cls._prepare_kwargs(kwargs)
        kwargs = prepared["kwargs"]

        try:
            return cast(T, cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {cls.__name__}: {e}") from e

Settings.register_kind(SettingsKind.TEMPLATE_ENGINE_SETTINGS, TemplateEngineSettings)