from typing import TypeVar
from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="SourceResolverSettings")

class SourceResolverSettings(Settings):
    n_threads: int | None = Field(
        default=None,
        description=(
            "Max number of threads. "
            "If None, let ThreadPoolExecutor choose a default."
        ),
        ge=1,
    )
    concurrent: bool = Field(
        default=True,
        description="Enable concurrent loading of sources when True; load sources sequentially when False."
    )

Settings.register_kind(SettingsKind.SOURCE_RESOLVER_SETTINGS, SourceResolverSettings)
