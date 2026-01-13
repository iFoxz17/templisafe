from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from templisafe.settings.variant_parser_settings import VariantParserSettings
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

class VariantParser:
    """Class for parsing and validating variants."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self, settings: VariantParserSettings) -> None:
        self._settings: VariantParserSettings = settings

    def _parse(self, b_index: int, b_name: str, b_value: Any) -> Binding:
        return Binding(index=b_index, name=b_name, value=b_value)

    def _parse_variants(self, variants_definition_list: list[dict[str, Any]]) -> VariantSet:
        settings: VariantParserSettings = self._settings
        
        variants_key: str = settings.variants_key
        implicit_counter: int = 1
        all_variants: dict[str, VariantExplicitModel] = {}

        for variant_definition in variants_definition_list:
            if variants_key not in variant_definition:
                raise IllegalVariantError(
                    f"Missing top-level variants key '{variants_key}' in definition {variant_definition}"
                )

            variant_context: Any = variant_definition[variants_key]
            
            # Multiple explicit variants each reporting variant_name and bindings keys
            if isinstance(variant_context, list):
                for expl_variant in variant_context:
                    if not (settings.variant_name_key in expl_variant and settings.bindings_key in expl_variant):
                        raise IllegalVariantError(f"Illegal variant definition: {expl_variant}")
                    var_name: str = expl_variant[settings.variant_name_key]
                    bindings: dict[str, Any] = expl_variant[settings.bindings_key]
                    
                    if var_name in all_variants:
                        raise IllegalVariantError(f"Duplicated variant: {var_name}")
                    all_variants[var_name] = VariantExplicitModel(name=var_name, bindings=bindings)
                continue
            
            if not isinstance(variant_context, dict):
                raise IllegalVariantError("Top-level variants context must be a list or a dict")
            
            # Single explicit variant reporting variant_name and bindings keys
            if settings.variant_name_key in variant_context and settings.bindings_key in variant_context:
                var_name: str = variant_context[settings.variant_name_key]
                bindings: dict[str, Any] = variant_context[settings.bindings_key]
                
                if var_name in all_variants:
                    raise IllegalVariantError(f"Duplicated variant: {var_name}")
                all_variants[var_name] = VariantExplicitModel(name=var_name, bindings=bindings)
                continue

            # Implicit variant
            for key, val in variant_context.items():
                if isinstance(val, dict):
                    # Implicit variant with name: top-level keys look like variant names
                    var_name: str = key
                    bindings: dict[str, Any] = val
                else:
                    # Implicit variant without name: key is a binding name
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

    def parse(self, variants_configs: list[dict[str, Any]]) -> VariantSet:
        return self._parse_variants(variants_configs)
