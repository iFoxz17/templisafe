from typing import TypeVar

from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="VariantParserSettings")

class VariantParserSettings(Settings):
    """Settings class for defining variant parsers."""

    variants_key: str = Field(
        "variants",
        description="The top-level key in the variants configuration"
    )
    default_variants_name: str = Field(
        "default",
        description="The default name assigned to implicit unnamed variants"
    )
    variant_name_key: str = Field(
        "name",
        description="The key for variant name in the variant configuration"
    )
    bindings_key: str = Field(
        "bindings",
        description="The key for bindings in the variant configuration"
    )

Settings.register_kind(SettingsKind.VARIANT_PARSER_SETTINGS, VariantParserSettings)