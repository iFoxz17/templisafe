from templisafe.executor.source_executor import SourceExecutor
from templisafe.settings.source import *
from templisafe.settings.source_executor_settings import SourceExecutorSettings

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SourceExecutorFactory:

    def __init__(self) -> None:
        pass

    def create(self, settings: SourceExecutorSettings) -> SourceExecutor:
        return SourceExecutor(settings=settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SourceExecutorManager:
    __slots__: tuple[str, ...] = ("_factory", "_executors")

    def __init__(self, executors: dict[SourceExecutorSettings, SourceExecutor] | None = None) -> None:
        self._factory: SourceExecutorFactory = SourceExecutorFactory()
        self._executors: dict[SourceExecutorSettings, SourceExecutor] = executors or {}
    
    def get_or_create(self, settings: SourceExecutorSettings) -> SourceExecutor:
        e: dict[SourceExecutorSettings, SourceExecutor] = self._executors
        if settings not in e:
            e[settings] = self._factory.create(settings)
        return e[settings]

    def __contains__(self, settings: SourceExecutorSettings) -> bool:
        return settings in self._executors