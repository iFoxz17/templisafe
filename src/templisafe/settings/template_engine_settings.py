from typing import Any, Callable, Type, TypeVar, cast
from pydantic import ValidationError
from enum import Enum
from overrides import overrides

from templisafe.settings.settings import Settings

T = TypeVar("T", bound="TemplateEngineSettings")


class TemplateEngineKind(str, Enum):
    JINJA = "jinja"
    DJANGO = "django"
    CUSTOM = "custom"


class TemplateEngineSettings(Settings):
    kind: TemplateEngineKind
    config: dict[str, Any]

    @classmethod
    def _prepare_kwargs(cls: Type[T], kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize 'kind' and 'config', perform subclass dispatch for CUSTOM kind,
        and return (target_cls, normalized_kwargs).

        Raises if multiple config sources are provided.
        """
       
        kind: Any = kwargs.get("kind")
        if kind is None:
            raise ValueError("Missing 'kind' field to determine template engine type.")

        if isinstance(kind, str):
            try:
                kwargs["kind"] = TemplateEngineKind(kind)
            except ValueError:
                raise ValueError(f"Invalid template engine kind: {kind!r}")

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

        # Subclass dispatch for CUSTOM kind
        if kwargs["kind"] == TemplateEngineKind.CUSTOM:
            if "extract_variables_func" not in kwargs or "render_func" not in kwargs:
                raise ValueError(
                    "CustomTemplateEngineSettings requires 'extract_variables_func' and 'render_func'."
                )
            target_cls: Type[T] = CustomTemplateEngineSettings  # type: ignore
        else:
            target_cls: Type[T] = cls

        return {"target_cls": target_cls, "kwargs": kwargs}


    @classmethod
    @overrides
    def _parse_config(cls: Type[T], config: dict[str, Any]) -> T:
        prepared: dict[str, Any] = cls._prepare_kwargs(config)
        target_cls: Type[T] = prepared["target_cls"]
        kwargs: dict[str, Any] = prepared["kwargs"]

        # Pydantic validation
        try:
            return cast(T, target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """Factory method to create the correct TemplateEngineSettings subclass."""
        prepared: dict[str, Any] = cls._prepare_kwargs(kwargs)
        target_cls: Type[T] = prepared["target_cls"]
        kwargs = prepared["kwargs"]

        try:
            return cast(T, target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e


class CustomTemplateEngineSettings(TemplateEngineSettings):
    """
    Settings for a custom template engine backed by user-provided callables.
    """

    extract_variables_func: Callable[[str, dict[str, Any]], set[str]]
    render_func: Callable[[str, dict[str, Any], dict[str, Any]], str]
