from typing import Type, TypeVar, Dict, Any
from pydantic import ValidationError

from templisafe.settings.settings import Settings

T = TypeVar("T", bound="TemplateParserSettings")


class TemplateParserSettings(Settings):
    """Concrete parser settings for text templates."""

    # -----------------------------
    # Factory / creation methods
    # -----------------------------
    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """
        Create a TemplateParserSettings instance.
        Kwargs are maintained for future extendibility.
        """
        
        try:
            return cls.model_validate({})
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {cls.__name__}: {e}") from e

    @classmethod
    def _parse_config(cls: Type[T], config: Dict[str, Any]) -> T:
        """Used by Settings.from_yaml/from_json/from_dict."""
        if not isinstance(config, dict):
            raise ValueError(f"Expected a dict, got {type(config).__name__}")
        return cls.create(**config)
