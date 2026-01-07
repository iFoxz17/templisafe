from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, model_validator, Field

from sqltemplater.loader.qparser import QParser
from sqltemplater.settings.parser.qparams_parser_settings import QVariantParserSettings
from sqltemplater.settings.parser.qparser_settings import QParserSettings
from sqltemplater.query.query_model import QVariantSet, QVariant, QBinding
from sqltemplater.exceptions.binding_error import IllegalVariantError, DuplicatedBindingError

VARIANT_DEFAULT_NAME: str = "default"

class QVariantModel(BaseModel):
    """Accepts either a single variant or a set of them."""
    variant_by_name: dict[str, dict[str, Any]] = Field(default_factory=dict)
    default_name: str

    @model_validator(mode="before")
    def normalize_variants(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            raise TypeError("No dict provided")
        
        input_data = values.get("variants", {})
        default_name = values.get("default_name", VARIANT_DEFAULT_NAME)

        if not isinstance(input_data, dict):
            raise TypeError("variants must be a dict")

        # Detect if it's a single parameterization (values are not dicts)
        if all(not isinstance(v, dict) for v in input_data.values()):
            values["variants"] = {default_name: input_data}
        # If it's already dict of dicts, leave as is
        elif all(isinstance(v, dict) for v in input_data.values()):
            values["variants"] = input_data
        else:
            raise TypeError("Mixed types in variants dict are not allowed")

        return values

class QVariantParser(QParser, ABC):
    """Abstract base class for parsing and validating QVariants."""

    __slots__: tuple[str, ...] = ('_settings',)
    
    def __init__(self, settings: QVariantParserSettings) -> None:
        super().__init__(settings)
       
    def _parse(self, b_index: int, b_name: str, b_value: Any) -> QBinding:
        return QBinding(index=b_index, name=b_name, value=b_value)
        
    def _parse_variants(self, variants_definition_dict: dict[str, Any]) -> QVariantSet:
        settings: QParserSettings = self._settings
        assert isinstance(settings, QVariantParserSettings)
        
        variants_key: str = settings.variants_key
        if variants_key not in variants_definition_dict:
            raise IllegalVariantError(f"Missing top-level variants key '{variants_key}'")
        
        variants_context_dict: Any = variants_definition_dict[variants_key]
        if not isinstance(variants_context_dict, dict):
            raise IllegalVariantError(f'Illegal variants definition')
        
        variants_models: QVariantModel
        try:
            variants_models = QVariantModel(
                variant_by_name=variants_context_dict,
                default_name=settings.default_variants_name
            )
        except Exception as e:
            raise IllegalVariantError(f'Illegal variants definition') from e 

        variants_by_name: dict[str, QVariant] = {}

        for (name, bindings_dict) in variants_models.variant_by_name.items():
            bindings_by_name: dict[str, QBinding] = {}

            for i, (b_name, b_value) in enumerate(bindings_dict.items()):
                if not isinstance(b_name, str):
                    raise IllegalVariantError(f'Illegal definition of binding {i}: {b_name} is not a string')
                binding: QBinding = self._parse(i, b_name, b_value)
                
                if b_name in bindings_by_name:        # This should never happen since dict cannot have duplicated keys
                    raise DuplicatedBindingError(b_name, bindings_by_name[b_name].index, i)
                bindings_by_name[b_name] = binding

            variants_by_name[name] = QVariant(bindings_by_name.values())

        return QVariantSet(list(variants_by_name.values()))
    
    @abstractmethod
    def _parse_raw(self, variants: str) -> dict[str, Any]:
        pass

    def parse(self, variants: str) -> QVariantSet:
        return self._parse_variants(self._parse_raw(variants))
        
