from typing import Any
from jinja2 import Environment

from sqltemplater.settings.environment_settings import EnvironmentSettings

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------

class EnvironmentFactory:
    """
    Factory class to create jinja2.Environment instances
    from a parsed EnvironmentSettings object.
    """

    def __init__(self) -> None:
        pass

    def create(self, settings: EnvironmentSettings) -> Environment:
        kwargs: dict[str, Any] = settings.model_dump(exclude_none=True)
        return Environment(**kwargs)

# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------

class EnvironmentManager:
    __slots__ = ("_factory", "_environments")

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
            
        