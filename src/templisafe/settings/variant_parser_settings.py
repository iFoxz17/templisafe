from typing import TypeVar

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="VariantParserSettings")

class VariantParserSettings(Settings):
    """Settings for parsers that handle variants."""
    variants_key: str
    default_variants_name: str
    variant_name_key: str
    bindings_key: str

Settings.register_kind(SettingsKind.VARIANT_PARSER_SETTINGS, VariantParserSettings)