from typing import TypeVar

from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="CompilerSettings")

_INDEX_KEY_DEFAULT: str = "_index"


class CompilerSettings(Settings):
    """Settings class for defining compilers."""

    index_key: str = Field(_INDEX_KEY_DEFAULT, description="The internal key for variables indexes")


Settings.register_kind(SettingsKind.COMPILER_SETTINGS, CompilerSettings)
