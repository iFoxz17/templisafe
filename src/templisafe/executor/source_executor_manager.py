from types import MappingProxyType
from collections.abc import Mapping
from tenacity import Retrying

from templisafe.exceptions.source_executor_error import UnsupportedExecutorStrategy
from templisafe.executor.sequential_source_executor import SequentialSourceExecutor
from templisafe.executor.thread_pool_source_executor import ThreadPoolSourceExecutor
from templisafe.settings.source_executor_settings import SourceExecutorSettings, SourceExecutorStrategy
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.executor.source_executor import SourceExecutor
from templisafe.executor.retrying_factory import RetryingFactory

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SourceExecutorFactory:
    """Creates `SourceExecutor` instances from source_executor settings."""

    __slots__: tuple[str, ...] = ("_retrying_factory", )

    _EXECUTOR_STRATEGY_MAP: Mapping[SourceExecutorStrategy, type[SourceExecutor]] = MappingProxyType(
            {
                SourceExecutorStrategy.SEQUENTIAL: SequentialSourceExecutor,
                SourceExecutorStrategy.THREAD_POOL: ThreadPoolSourceExecutor
            }
        )

    def __init__(self, retrying_factory: RetryingFactory | None = None) -> None:
        self._retrying_factory: RetryingFactory = retrying_factory or RetryingFactory()

    def create(self, settings: SourceExecutorSettings) -> SourceExecutor:
        """Create a `SourceExecutor` instance for the given settings."""

        strategy: SourceExecutorStrategy = settings.actual_strategy
        executor_type: type[SourceExecutor] | None = self._EXECUTOR_STRATEGY_MAP.get(strategy)
        if executor_type is None:
            raise UnsupportedExecutorStrategy(strategy)
        
        retrying: Retrying = self._retrying_factory.create(settings.resilience_policy)
        return executor_type(settings=settings, retrying=retrying)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SourceExecutorManager:
    """Manages the retrieval of `SourceExecutor` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_executors")

    def __init__(
            self, 
            settings: ManagerSettings,
            factory: SourceExecutorFactory | None = None,
            executors: dict[SourceExecutorSettings, SourceExecutor] | None = None
            ) -> None:
        self._settings: ManagerSettings = settings
        self._factory: SourceExecutorFactory = factory or SourceExecutorFactory()
        self._executors: dict[SourceExecutorSettings, SourceExecutor] = executors or {}
    
    def get_or_create(self, settings: SourceExecutorSettings) -> SourceExecutor:
        """Return a `SourceExecutor` instance according to the given settings."""
        
        e: dict[SourceExecutorSettings, SourceExecutor] = self._executors
        if settings in e:
            return e[settings]
        
        executor: SourceExecutor = self._factory.create(settings)
        if self._settings.cache:
            e[settings] = executor
        return executor

    def __contains__(self, settings: SourceExecutorSettings) -> bool:
        """Return whether a `SourceExecutor` instance for the given settings is cached."""
        return settings in self._executors