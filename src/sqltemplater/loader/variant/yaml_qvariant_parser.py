import yaml
from overrides import overrides
from typing import Any

from sqltemplater.settings.parser.qparams_parser_settings import YamlQVariantParserSettings
from sqltemplater.exceptions.binding_error import IllegalVariantError
from sqltemplater.loader.variant.qvariant_parser import QVariantParser

class YamlQVariantParser(QVariantParser):

    def __init__(self, settings: YamlQVariantParserSettings) -> None:
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