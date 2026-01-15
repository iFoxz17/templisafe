from typing import TypeVar

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="TemplateParserSettings")

class TemplateParserSettings(Settings):
    """Concrete parser settings for text templates."""
    pass

Settings.register_kind(SettingsKind.TEMPLATE_PARSER_SETTINGS, TemplateParserSettings)
