from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from templisafe.exceptions.variant_error import IllegalVariantError
from templisafe.settings.variant_parser_settings import VariantParserSettings


class TemplateInput(BaseModel):
    """Public input model for an already available template string."""

    template: str

    model_config = ConfigDict(frozen=True)


class SchemaInput(BaseModel):
    """Public input model for a schema configuration document."""

    schema_: dict[str, Any] = Field(alias="schema")

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    def to_config(self) -> dict[str, Any]:
        """Return the canonical schema configuration mapping."""
        return self.model_dump(by_alias=True)


class VariantInput(BaseModel):
    """Public input model for one named variant."""

    name: str
    bindings: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def _validate_name(self) -> "VariantInput":
        if not self.name:
            raise ValueError("Variant name cannot be empty")
        return self


class VariantSetInput(BaseModel):
    """Public input model for one or more named variants."""

    variants: VariantInput | list[VariantInput] | dict[str, Any]

    model_config = ConfigDict(frozen=True, extra="forbid")

    @classmethod
    def from_config(cls, config: dict[str, Any], settings: VariantParserSettings) -> "VariantSetInput":
        """Create variant set input by adapting configurable field names to canonical names."""

        variants_key = settings.variants_key
        if variants_key not in config:
            raise IllegalVariantError(f"Missing top-level variants key '{variants_key}' in definition {config}")

        try:
            return cls.model_validate(
                {
                    "variants": cls._normalize_context(
                        config[variants_key],
                        variant_name_key=settings.variant_name_key,
                        bindings_key=settings.bindings_key,
                    )
                }
            )
        except (TypeError, ValueError, ValidationError) as e:
            raise IllegalVariantError(f"Illegal variant definition: {config}") from e

    @staticmethod
    def _normalize_context(
        context: Any,
        *,
        variant_name_key: str,
        bindings_key: str,
    ) -> Any:
        if isinstance(context, list):
            return [
                VariantSetInput._normalize_explicit_variant(item, variant_name_key, bindings_key) for item in context
            ]
        if isinstance(context, dict):
            if variant_name_key in context or bindings_key in context:
                return VariantSetInput._normalize_explicit_variant(context, variant_name_key, bindings_key)
            return context
        return context

    @staticmethod
    def _normalize_explicit_variant(
        value: Any,
        variant_name_key: str,
        bindings_key: str,
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError(f"Illegal variant definition: {value}")

        if variant_name_key not in value:
            raise ValueError(f"Missing variant name key '{variant_name_key}' in definition {value}")
        if bindings_key not in value:
            raise ValueError(f"Missing variant bindings key '{bindings_key}' in definition {value}")

        name = value[variant_name_key]
        bindings = value[bindings_key]
        if not isinstance(name, str) or not name:
            raise ValueError(f"Illegal variant name: {name}")
        if not isinstance(bindings, dict):
            raise ValueError(f"Illegal variant bindings: {bindings}")

        return {
            "name": name,
            "bindings": bindings,
        }

    def normalize(self, default_name: str) -> tuple[VariantInput, ...]:
        """Return canonical variant definitions for explicit and implicit document styles."""

        variants = self.variants
        if isinstance(variants, VariantInput):
            return (variants,)
        if isinstance(variants, list):
            return tuple(variants)

        if not variants:
            return (VariantInput(name=default_name, bindings={}),)

        if all(isinstance(value, dict) for value in variants.values()):
            return tuple(VariantInput(name=name, bindings=bindings) for name, bindings in variants.items())

        return (VariantInput(name=default_name, bindings=variants),)


__all__ = [
    "TemplateInput",
    "SchemaInput",
    "VariantInput",
    "VariantSetInput",
]
