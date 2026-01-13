from typing import Type, TypeVar, Dict, Any
from pydantic import ValidationError

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="TemplateParserSettings")

class TemplateParserSettings(Settings):
    """Concrete parser settings for text templates."""
    pass

Settings.register_kind(SettingsKind.TEMPLATE_PARSER_SETTINGS, TemplateParserSettings)
