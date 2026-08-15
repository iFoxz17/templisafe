from typing import Any

from templisafe.template.template_model import VariantSet
from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.parser.variant.variant_parser_manager import VariantParserManager
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.util import DEFAULT_MANAGER_SETTINGS

_VARIANTS_KEY_KEY: str = 'variants_key'
_DEFAULT_VARIANTS_KEY_KEY: str = 'default_variants_name'
_VARIANTS_NAME_KEY_KEY: str = 'variant_name_key'
_BINDINGS_KEY_KEY: str = 'bindings_key'

VARIANT_PARSER_SETTINGS_YAML: str = f"""
{_VARIANTS_KEY_KEY}: variants
{_DEFAULT_VARIANTS_KEY_KEY}: default
{_VARIANTS_NAME_KEY_KEY}: name
{_BINDINGS_KEY_KEY}: bindings
"""

class VariantLoader:

    __slots__: tuple[str, ...] = ('_default_settings', '_manager',)

    def __init__(self, default_settings: VariantParserSettings | None = None) -> None:
        self._default_settings: VariantParserSettings = default_settings or VariantParserSettings.from_yaml(VARIANT_PARSER_SETTINGS_YAML)
        self._manager: VariantParserManager = VariantParserManager(
            settings=DEFAULT_MANAGER_SETTINGS
        )

    def _resolve_settings(self, parser_settings: VariantParserSettings | None = None) -> VariantParserSettings:
        return parser_settings or self._default_settings

    def load(self, variants_configs: list[dict[str, Any]], parser_settings: VariantParserSettings | None = None) -> VariantSet:
        parser_settings = self._resolve_settings(parser_settings)
        parser: VariantParser = self._manager.get_or_create(parser_settings)
        return parser.parse(variants_configs)
