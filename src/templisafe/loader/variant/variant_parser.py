from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict

from templisafe.settings.parser.variant_parser_settings import VariantParserSettings
from templisafe.settings.parser.parser_settings import ParserSettings
from templisafe.template.template_model import VariantSet, Variant, Binding
from templisafe.exceptions.binding_error import IllegalVariantError

# ---------------------------------------------------------------------------
# Variant models (validation only)
# ---------------------------------------------------------------------------

class VariantExplicitModel(BaseModel):
    """Represents a named variant with its bindings (explicit)."""
    name: str
    bindings: dict[str, Any] = Field(...)

    model_config = ConfigDict(frozen=True)

# ---------------------------------------------------------------------------
# Variant parser
# ---------------------------------------------------------------------------

class VariantParser(ABC):
    """Abstract base class for parsing and validating variants."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self, settings: VariantParserSettings) -> None:
        self._settings: VariantParserSettings = settings

    def _parse(self, b_index: int, b_name: str, b_value: Any) -> Binding:
        return Binding(index=b_index, name=b_name, value=b_value)

    def _parse_variants(self, variants_definition_list: list[dict[str, Any]]) -> VariantSet:
        settings: ParserSettings = self._settings
        assert isinstance(settings, VariantParserSettings)

        variants_key: str = settings.variants_key
        implicit_counter: int = 1
        all_variants: dict[str, VariantExplicitModel] = {}

        for variant_definition in variants_definition_list:
            if variants_key not in variant_definition:
                raise IllegalVariantError(
                    f"Missing top-level variants key '{variants_key}' in definition {variant_definition}"
                )

            variant_context: Any = variant_definition[variants_key]
            if not isinstance(variant_context, dict):
                raise IllegalVariantError("Top-level variants context must be a dict")

            # If top-level keys look like variant names
            for key, val in variant_context.items():
                if isinstance(val, dict):
                    # Explicit variant
                    var_name: str = key
                    bindings: dict[str, Any] = val
                else:
                    # Implicit variant: key is a binding name
                    var_name: str = f"{settings.default_variants_name}_{implicit_counter}"
                    bindings: dict[str, Any] = variant_context
                    implicit_counter += 1
                    
                    # Only one implicit variant per top-level dict
                    if var_name in all_variants:
                        raise IllegalVariantError(f"Duplicated variant: {var_name}")
                    all_variants[var_name] = VariantExplicitModel(name=var_name, bindings=bindings)
                    break

                if var_name in all_variants:
                    raise IllegalVariantError(f"Duplicated variant: {var_name}")

                all_variants[var_name] = VariantExplicitModel(name=var_name, bindings=bindings)

        # Convert to VariantSet
        variant_objs: list[Variant] = []
        for v_model in all_variants.values():
            bindings_list: list[Binding] = [
                self._parse(i, b_name, b_value)
                for i, (b_name, b_value) in enumerate(v_model.bindings.items())
            ]
            variant_objs.append(Variant(name=v_model.name, bindings=bindings_list))

        return VariantSet(variant_objs)


    @abstractmethod
    def _parse_raw(self, variants: str) -> dict[str, Any]:
        """Parse a raw variant string into a dictionary with the top-level variants key."""
        pass

    def parse(self, variants: list[str]) -> VariantSet:
        variants_dicts: list[dict[str, Any]] = [self._parse_raw(v) for v in variants]
        return self._parse_variants(variants_dicts)
