from typing import Type, TypeVar, Dict, Any, cast
from pydantic import ValidationError
from overrides import overrides

from templisafe.settings.settings import Settings
from templisafe.exceptions.settings_error import SettingsError

T = TypeVar("T", bound="RendererSettings")

class RendererSettings(Settings):
    index_key: str

    @classmethod
    @overrides
    def _parse_config(cls: Type[T], config: Dict[str, Any]) -> T:
        """Normalize and validate a config dict into a RendererSettings instance."""
        if not isinstance(config, dict):
            raise SettingsError(f"Expected a dict, got {type(config).__name__}")

        # Only one required field here
        if "index_key" not in config or config["index_key"] is None:
            raise ValueError("Missing 'index_key' field")

        # Validate using Pydantic
        try:
            return cast(T, cls.model_validate(config))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {cls.__name__}: {e}") from e

    @classmethod
    def create(cls: Type[T], **kwargs: Any) -> T:
        """Factory method to create RendererSettings from kwargs."""
        return cls._parse_config(kwargs)