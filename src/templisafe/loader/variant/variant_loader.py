from overrides import overrides
from typing import Any

from templisafe.template.template_model import VariantSet
from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.source.source import Source
from templisafe.loader.variant.variant_parser_manager import VariantParserManager
from templisafe.settings.parser.parser_settings import ParserSettings
from templisafe.settings.parser.variant_parser_settings import YamlVariantParserSettings, VariantParserSettings
from templisafe.util.util import ContentType
from templisafe.exceptions.binding_error import IllegalParamsDefinitionError, UnsupportedQVariantParserError

_PARAMS_KEY_KEY: str = 'params_key'
_DEFAULT_QVARIANT_KEY_KEY: str = 'default_variant_name'

VARIANT_PARSER_SETTINGS_YAML: str = f"""
default_diagnostic_policy: RAISE_WARNINGS
parser_type: YAML
{_PARAMS_KEY_KEY}: params
{_DEFAULT_QVARIANT_KEY_KEY}: default
"""

class VariantLoader:

    __slots__: tuple[str, ...] = ('_default_settings', '_manager',)

    def __init__(self, default_settings: VariantParserSettings | None = None) -> None:
        self._default_settings: VariantParserSettings = default_settings or VariantParserSettings.from_yaml(VARIANT_PARSER_SETTINGS_YAML)
        self._manager: VariantParserManager = VariantParserManager()

    def _resolve_settings(self, parser_settings: VariantParserSettings | None = None) -> VariantParserSettings:
        return parser_settings or self._default_settings

    def load(self, variants_sources: list[Source], parser_settings: VariantParserSettings | None = None) -> VariantSet:
        parser_settings = self._resolve_settings(parser_settings)
        parser: VariantParser = self._manager.get_or_create(parser_settings)
        variants_str: list[str] = [vs.read() for vs in variants_sources]
        return parser.parse(variants_str)