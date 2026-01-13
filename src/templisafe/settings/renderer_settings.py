from typing import TypeVar

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="RendererSettings")

class RendererSettings(Settings):
    index_key: str

Settings.register_kind(SettingsKind.RENDERER_SETTINGS, RendererSettings)

