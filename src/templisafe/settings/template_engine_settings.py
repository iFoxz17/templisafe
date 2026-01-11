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
            
        # If config is a string, parse it
        config: Any = kwargs.get("config", {})
        if isinstance(config, str):
            import yaml
            try:
                config = yaml.safe_load(kwargs['config'])
            except yaml.YAMLError as e:
                raise e

        # At this point 'config' must exist and be a dict    
        if not isinstance(config, dict):
            raise ValueError(f"Expected 'config' to be a dict, found {type(config).__name__}")
        kwargs["config"] = config

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
    """
    Settings for a custom template engine backed by user-provided callables.

    This settings class allows users to plug in arbitrary template logic
    without implementing a concrete `TemplateEngine` subclass.

    Required callables:

    - `extract_variables_func(template: str, config: dict[str, Any]) -> set[str]`
        A callable that receives the template string and the engine configuration,
        and returns the set of variable names used by the template.

    - `render_func(
            template: str,
            variables: dict[str, Any],
            config: dict[str, Any]
        ) -> str`
        A callable that receives the template string, a mapping of variable values,
        and the engine configuration, and returns the rendered string.

    The `config` field is passed unchanged to both callables and can be used
    to control custom rendering behavior.
    """

    extract_variables_func: Callable[[str, dict[str, Any]], set[str]]
    render_func: Callable[[str, dict[str, Any], dict[str, Any]], str]

    # Make the model immutable and forbid extra fields
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
