from typing import TypeVar

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="CompilerSettings")

class CompilerSettings(Settings):
    index_key: str

Settings.register_kind(SettingsKind.COMPILER_SETTINGS, CompilerSettings)