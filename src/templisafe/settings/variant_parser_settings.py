from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind


class VariantParserSettings(Settings):
    """Settings class for defining variant parsers."""

    default_variants_name: str = Field("default", description="The default name assigned to implicit unnamed variants")


Settings.register_kind(SettingsKind.VARIANT_PARSER_SETTINGS, VariantParserSettings)
