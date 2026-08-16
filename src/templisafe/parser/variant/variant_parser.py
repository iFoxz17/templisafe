from typing import Any

from templisafe.exceptions.variant_error import IllegalVariantError
from templisafe.input import VariantInput, VariantSetInput
from templisafe.parser.config.config_parser import Config
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.template.template_model import Binding, Variant, VariantSet


class VariantParser:
    """Parses raw variant configurations into `VariantSet` objects."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self, settings: VariantParserSettings) -> None:
        self._settings: VariantParserSettings = settings

    def _create_binding(self, index: int, name: str, value: Any) -> Binding:
        return Binding(index=index, name=name, value=value)

    def _create_variant(self, model: VariantInput) -> Variant:
        bindings = [
            self._create_binding(index, binding_name, binding_value)
            for index, (binding_name, binding_value) in enumerate(model.bindings.items())
        ]
        return Variant(name=model.name, bindings=bindings)

    def _parse_document(self, config: dict[str, Any], default_name: str) -> tuple[VariantInput, ...]:
        variant_set_input = VariantSetInput.from_config(config, self._settings)
        return variant_set_input.normalize(default_name)

    def parse(self, variant_configs: Config) -> VariantSet:
        """
        Parse one or more variant configuration dictionaries into a `VariantSet`.

        Supported document styles:

        - explicit single variant: `{variants: {name: v1, bindings: {...}}}`
        - explicit variant list: `{variants: [{name: v1, bindings: {...}}]}`
        - implicit named variants: `{variants: {v1: {...}, v2: {...}}}`
        - implicit unnamed variant: `{variants: {x: 1, y: 2}}`
        """

        configs = variant_configs if isinstance(variant_configs, list) else [variant_configs]
        if not all(isinstance(config, dict) for config in configs):
            raise IllegalVariantError(f"Expecting variant configurations to be a list of dicts, found: {configs}")

        parsed: dict[str, VariantInput] = {}
        implicit_counter = 1
        for config in configs:
            default_name = f"{self._settings.default_variants_name}_{implicit_counter}"
            models = self._parse_document(config, default_name)
            if any(model.name == default_name for model in models):
                implicit_counter += 1

            for model in models:
                if model.name in parsed:
                    raise IllegalVariantError(f"Duplicated variant: {model.name}")
                parsed[model.name] = model

        return VariantSet(self._create_variant(model) for model in parsed.values())
