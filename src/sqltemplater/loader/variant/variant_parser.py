from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, model_validator, Field, ConfigDict

from sqltemplater.loader.parser import Parser
from sqltemplater.settings.parser.variant_parser_settings import VariantParserSettings
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.template.template_model import VariantSet, Variant, Binding
from sqltemplater.exceptions.binding_error import IllegalVariantError

VARIANT_DEFAULT_NAME: str = "default"

class VariantModel(BaseModel):
    """Accepts either a single variant or a set of them."""

    variant_by_name: dict[str, dict[str, Any]] = Field(default_factory=dict)
    default_name: str

    model_config = ConfigDict({
        "frozen": True
    })

    @model_validator(mode="before")
    def normalize_variants(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            raise TypeError("No dict provided")
        
        input_data = values.get("variant_by_name", {})
        default_name = values.get("default_name", VARIANT_DEFAULT_NAME)

        if not isinstance(input_data, dict):
            raise TypeError("variant_by_name must be a dict")

        # Detect if it's a single parameterization (values are not dicts)
        if all(not isinstance(v, dict) for v in input_data.values()):
            values["variant_by_name"] = {default_name: input_data}
        # If it's already dict of dicts, leave as is
        elif all(isinstance(v, dict) for v in input_data.values()):
            values["variant_by_name"] = input_data
        else:
            raise TypeError("Mixed types in variant_by_name dict are not allowed")

        return values

class VariantParser(Parser, ABC):
    """Abstract base class for parsing and validating QVariants."""

    __slots__: tuple[str, ...] = ('_settings',)
    
    def __init__(self, settings: VariantParserSettings) -> None:
        super().__init__(settings)
       
    def _parse(self, b_index: int, b_name: str, b_value: Any) -> Binding:
        return Binding(index=b_index, name=b_name, value=b_value)
        
    def _parse_variants(self, variants_definition_dict: dict[str, Any]) -> VariantSet:
        settings: ParserSettings = self._settings
        assert isinstance(settings, VariantParserSettings)
        
        variants_key: str = settings.variants_key
        if variants_key not in variants_definition_dict:
            raise IllegalVariantError(f"Missing top-level variants key '{variants_key}'")
        
        variants_context_dict: Any = variants_definition_dict[variants_key]
        if not isinstance(variants_context_dict, dict):
            raise IllegalVariantError(f'Illegal variants definition')
        
        variants_models: VariantModel
        try:
            variants_models = VariantModel(
                variant_by_name=variants_context_dict,
                default_name=settings.default_variants_name
            )
        except Exception as e:
            raise IllegalVariantError(f'Illegal variants definition') from e 

        variants_by_name: dict[str, Variant] = {}

        for (variant_name, bindings_dict) in variants_models.variant_by_name.items():
            bindings_by_name: dict[str, Binding] = {}

            for i, (b_name, b_value) in enumerate(bindings_dict.items()):
                if not isinstance(b_name, str):
                    raise IllegalVariantError(f'Illegal definition of binding {i}: {b_name} is not a string')
                binding: Binding = self._parse(i, b_name, b_value)
                
                # b_name cannot be duplicated since it is a dict key
                bindings_by_name[b_name] = binding

            variants_by_name[variant_name] = Variant(
                name=variant_name,
                bindings=bindings_by_name.values()
            )

        return VariantSet(list(variants_by_name.values()))
    
    @abstractmethod
    def _parse_raw(self, variants: str) -> dict[str, Any]:
        pass

    def parse(self, variants: str) -> VariantSet:
        return self._parse_variants(self._parse_raw(variants))
        
