from typing import Any
from jinja2 import Environment

from templisafe.settings.environment_settings import EnvironmentSettings

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------

class EnvironmentFactory:
    """Creates Jinja2 Environment instances from EnvironmentSettings."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def create(self, settings: EnvironmentSettings) -> Environment:
        kwargs: dict[str, Any] = settings.model_dump(exclude_none=True)
        return Environment(**kwargs)

# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------

class EnvironmentManager:
    """Manages cached Jinja2 Environment instances by their settings."""

    __slots__: tuple[str, ...] = ("_factory", "_environments")

    def __init__(
            self, 
            environments: dict[EnvironmentSettings, Environment] | None = None
            ) -> None:
        self._factory: EnvironmentFactory = EnvironmentFactory()
        self._environments: dict[EnvironmentSettings, Environment] = environments or {}

    def get_or_create(self, settings: EnvironmentSettings) -> Environment:
        envs: dict[EnvironmentSettings, Environment] = self._environments    
        if settings not in envs:
            envs[settings] = self._factory.create(settings)
        return envs[settings]
            
        