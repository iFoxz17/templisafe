from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from templisafe.exceptions.variant_error import IllegalVariantError

VARIANTS_KEY = "variants"
VARIANT_NAME_KEY = "name"
VARIANT_BINDINGS_KEY = "bindings"


class TemplateInput(BaseModel):
    """Public input model for an already available template string."""

    template: str

    model_config = ConfigDict(frozen=True)


class VariableInput(BaseModel):
    """Public input model for one schema variable definition."""

    type: str
    default: Any = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)


class SchemaInput(BaseModel):
    """Public input model for a canonical schema document."""

    schema_: dict[str, str | VariableInput] = Field(alias="schema")

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    def to_config(self) -> dict[str, Any]:
        """Return the canonical schema configuration mapping."""
        return self.model_dump(by_alias=True, exclude_unset=True)


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
    def from_config(cls, config: dict[str, Any]) -> "VariantSetInput":
        """Create variant set input from the canonical variant document shape."""

        if VARIANTS_KEY not in config:
            raise IllegalVariantError(f"Missing top-level variants key '{VARIANTS_KEY}' in definition {config}")

        try:
            return cls.model_validate(
                {
                    "variants": cls._normalize_context(
                        config[VARIANTS_KEY],
                    )
                }
            )
        except (TypeError, ValueError, ValidationError) as e:
            raise IllegalVariantError(f"Illegal variant definition: {config}") from e

    @staticmethod
    def _normalize_context(
        context: Any,
    ) -> Any:
        if isinstance(context, list):
            return [VariantSetInput._normalize_explicit_variant(item) for item in context]
        if isinstance(context, dict):
            if VARIANT_NAME_KEY in context or VARIANT_BINDINGS_KEY in context:
                return VariantSetInput._normalize_explicit_variant(context)
            return context
        return context

    @staticmethod
    def _normalize_explicit_variant(
        value: Any,
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError(f"Illegal variant definition: {value}")

        if VARIANT_NAME_KEY not in value:
            raise ValueError(f"Missing variant name key '{VARIANT_NAME_KEY}' in definition {value}")
        if VARIANT_BINDINGS_KEY not in value:
            raise ValueError(f"Missing variant bindings key '{VARIANT_BINDINGS_KEY}' in definition {value}")

        name = value[VARIANT_NAME_KEY]
        bindings = value[VARIANT_BINDINGS_KEY]
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
    "VariableInput",
    "SchemaInput",
    "VariantInput",
    "VariantSetInput",
]
