from typing import TypeVar
from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="RendererSettings")

class RendererSettings(Settings):
    """Settings class for defining compilers."""

    index_key: str = Field(..., description="The internal key for bindings indexes")

Settings.register_kind(SettingsKind.RENDERER_SETTINGS, RendererSettings)

