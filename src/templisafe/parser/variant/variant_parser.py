from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from templisafe.exceptions.variant_error import IllegalVariantError
from templisafe.parser.config.config_parser import Config
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.template.template_model import Binding, Variant, VariantSet

# ---------------------------------------------------------------------------
# Variant models (validation only)
# ---------------------------------------------------------------------------


class VariantExplicitModel(BaseModel):
    """Represents an explicit named variant with its bindings."""

    name: str
    bindings: dict[str, Any] = Field(...)

    model_config = ConfigDict(frozen=True)


# ---------------------------------------------------------------------------
# Variant parser
# ---------------------------------------------------------------------------


class VariantParser:
    """Parses raw variants definitions `Variants` objects."""

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
                    explicit_name: str = expl_variant[settings.variant_name_key]
                    explicit_bindings: dict[str, Any] = expl_variant[settings.bindings_key]

                    if explicit_name in all_variants:
                        raise IllegalVariantError(f"Duplicated variant: {explicit_name}")
                    all_variants[explicit_name] = VariantExplicitModel(
                        name=explicit_name,
                        bindings=explicit_bindings,
                    )
                continue

            if not isinstance(variant_context, dict):
                raise IllegalVariantError("Top-level variants context must be a list or a dict")

            # Single explicit variant reporting variant_name and bindings keys
            if settings.variant_name_key in variant_context and settings.bindings_key in variant_context:
                explicit_name = variant_context[settings.variant_name_key]
                explicit_bindings = variant_context[settings.bindings_key]

                if explicit_name in all_variants:
                    raise IllegalVariantError(f"Duplicated variant: {explicit_name}")
                all_variants[explicit_name] = VariantExplicitModel(
                    name=explicit_name,
                    bindings=explicit_bindings,
                )
                continue

            # Implicit variant
            for key, val in variant_context.items():
                if isinstance(val, dict):
                    # Implicit variant with name: top-level keys look like variant names
                    implicit_name: str = key
                    implicit_bindings: dict[str, Any] = val
                else:
                    # Implicit variant without name: key is a binding name
                    implicit_name = f"{settings.default_variants_name}_{implicit_counter}"
                    implicit_bindings = variant_context
                    implicit_counter += 1

                    # Only one implicit variant per top-level dict
                    if implicit_name in all_variants:
                        raise IllegalVariantError(f"Duplicated variant: {implicit_name}")
                    all_variants[implicit_name] = VariantExplicitModel(
                        name=implicit_name,
                        bindings=implicit_bindings,
                    )
                    break

                if implicit_name in all_variants:
                    raise IllegalVariantError(f"Duplicated variant: {implicit_name}")

                all_variants[implicit_name] = VariantExplicitModel(
                    name=implicit_name,
                    bindings=implicit_bindings,
                )

        # Convert to VariantSet
        variant_objs: list[Variant] = []
        for v_model in all_variants.values():
            bindings_list: list[Binding] = [
                self._parse(i, b_name, b_value) for i, (b_name, b_value) in enumerate(v_model.bindings.items())
            ]
            variant_objs.append(Variant(name=v_model.name, bindings=bindings_list))

        return VariantSet(variant_objs)

    def parse(self, variant_configs: Config) -> VariantSet:
        """
        Parse a list of variant configuration dictionaries into a `VariantSet`.

        The input supports three types of variant definitions:

        1. **Explicit variants**
        A dictionary with the top-level `variants_key` containing a single variant or a list
        of variants. Each variant must include `variant_name_key` and `bindings_key`.

        Examples:
        ```python
        # Single explicit variant
        {
            "variants": {
                "variant_name": "v1",
                "bindings": {"x": 1, "y": 2}
            }
        }

        # Multiple explicit variants
        {
            "variants": [
                {"variant_name": "v1", "bindings": {"x": 1}},
                {"variant_name": "v2", "bindings": {"x": 2, "y": 3}}
            ]
        }
        ```

        2. **Implicit variants**
        A dictionary where top-level keys may act as variant names mapping to
        binding dictionaries, or where the dictionary itself represents unnamed bindings.
        Unnamed variants are automatically assigned names like `default_1`, `default_2`, etc.

        Examples:
        ```python
        # Implicit named variants: top-level keys as variant names
        {
            "v1": {"x": 1, "y": 2},
            "v2": {"x": 3}
        }

        # Single implicit unnamed variant
        {
            "x": 1,
            "y": 2
        }
        # Becomes variant named "default_1" with bindings {"x": 1, "y": 2}
        ```

        3. **Mixed definitions**
        Multiple variant dictionaries can be passed in a list. Each dictionary
        can contain explicit or implicit variants.

        Parameters
        ----------
        variants_configs : Config
            A list of variant configuration dictionaries to parse (or a single one).
            Each dictionary should define variant(s) according to one of schemas described above.

        Returns
        -------
        VariantSet
            A `VariantSet` object containing parsed `Variant` instances with their
            respective `Binding` objects.

        Raises
        ------
        VariantError
            If the input is not a list of dictionaries, or if a variant definition is
            malformed, duplicated or missing required keys.
        """

        if not isinstance(variant_configs, list):
            variant_configs = [variant_configs]

        if not all([isinstance(vc, dict) for vc in variant_configs]):
            raise IllegalVariantError(
                f"Expecting variants configurations to be a list of dict, found: {variant_configs}"
            )
        return self._parse_variants(variant_configs)
