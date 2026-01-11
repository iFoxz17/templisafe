import yaml
from overrides import overrides
from typing import Any

from templisafe.exceptions.binding_error import IllegalVariantError
from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.settings.parser.variant_parser_settings import YamlVariantParserSettings

class YamlVariantParser(VariantParser):

    def __init__(self, settings: YamlVariantParserSettings) -> None:
        super().__init__(settings)

    @overrides
    def _parse_raw(self, variants: str) -> dict[str, Any]:
        try:
            data: Any = yaml.safe_load(variants)
        except yaml.YAMLError as e:
            raise IllegalVariantError(f"Failed to parse YAML: {e}") from e

        if not isinstance(data, dict):
            raise IllegalVariantError("Parsed YAML variants is not a dictionary")

        return data