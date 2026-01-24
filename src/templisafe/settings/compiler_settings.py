from typing import TypeVar
from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="CompilerSettings")

class CompilerSettings(Settings):
    """Settings class for defining compilers."""

    index_key: str = Field(..., description="The internal key for variables indexes")

Settings.register_kind(SettingsKind.COMPILER_SETTINGS, CompilerSettings)