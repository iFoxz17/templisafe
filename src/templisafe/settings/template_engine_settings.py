from typing import Any, Callable
from pydantic import BaseModel, ConfigDict, ValidationError
from enum import Enum


class TemplateEngineKind(str, Enum):
    JINJA = "jinja"
    DJANGO = "django"
    CUSTOM = "custom"


class TemplateEngineSettings(BaseModel):
    kind: TemplateEngineKind
    config: dict[str, Any]

    # Make the model immutable and forbid extra fields
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )

    @classmethod
    def create(cls, **kwargs) -> "TemplateEngineSettings":
        """Factory method to create a TemplateEngineSettings instance."""

        kind: Any = kwargs.get("kind")
        if kind is None:
            raise ValueError("Missing 'kind' field to determine template engine type.")

        # Convert string to TemplateEngineKind enum if necessary
        if isinstance(kind, str):
            try:
                kwargs["kind"] = TemplateEngineKind(kind)
            except ValueError:
                raise ValueError(f"Invalid template engine kind: {kind!r}")

        # Ensure 'config' exists and is a dict
        config: Any = kwargs.get("config", {})
        if not isinstance(config, dict):
            raise ValueError(f"Expected 'config' to be a dict, found {type(config).__name__}")

        # Determine correct subclass if kind is CUSTOM
        if kwargs["kind"] == TemplateEngineKind.CUSTOM:
            if "extract_variables_func" not in kwargs or "render_func" not in kwargs:
                raise ValueError(
                    "CustomTemplateEngineSettings requires 'extract_variables_func' and 'render_func'."
                )
            target_cls = CustomTemplateEngineSettings
        else:
            target_cls = cls

        # Validate using Pydantic
        try:
            return target_cls.model_validate(kwargs)
        except ValidationError as e:
            raise ValueError(
                f"Invalid fields for {target_cls.__name__}: {e}"
            ) from e


class CustomTemplateEngineSettings(TemplateEngineSettings):
    extract_variables_func: Callable[[str], set[str]]
    render_func: Callable[[str, dict[str, Any]], str]

    # Make the model immutable and forbid extra fields
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
