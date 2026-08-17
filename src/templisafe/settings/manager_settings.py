from typing import TypeVar

from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="ManagerSettings")


class ManagerSettings(Settings):
    """Settings class for defining component managers."""

    cache: bool = Field(default=True, description="True to enable components caching.")


Settings.register_kind(SettingsKind.MANAGER_SETTINGS, ManagerSettings)
