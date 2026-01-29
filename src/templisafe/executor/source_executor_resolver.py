from templisafe.executor.source_executor import SourceExecutor
from templisafe.executor.source_executor_manager import SourceExecutorManager
from templisafe.settings.source_executor_settings import SourceExecutorSettings

class SourceExecutorResolver:
    """Resolves `SourceExecutor` instances."""

    __slots__: tuple[str, ...] = ("_default_settings", "_source_executor_manager")

    def __init__(
            self, 
            default_settings: SourceExecutorSettings,
            source_executor_manager: SourceExecutorManager
            ) -> None:
        self._default_settings: SourceExecutorSettings = default_settings
        self._source_executor_manager: SourceExecutorManager = source_executor_manager

    @property
    def default_settings(self) -> SourceExecutorSettings:
        return self._default_settings
        
    def resolve(self, source_executor: SourceExecutor | SourceExecutorSettings | None = None) -> SourceExecutor:
        """
        Resolve a `SourceExecutor` instance.

        This method supports three scenarios based on the type of the `source_executor` argument:
        1. If it is already a `SourceExecutor`, it is returned as-is.
        2. If it is a `SourceExecutorSettings`, a `SourceExecutor` based on the given settings is returned.
        3. If it is None, a `SourceExecutor` with default settings is returned.

        Parameters
        ----------
        source_executor : SourceExecutor | SourceExecutorSettings | None
            Either an existing source executor, its settings or None to use the default executor.

        Returns
        -------
        SourceExecutor
            The resolved source executor instance.
        """

        if isinstance(source_executor, SourceExecutor):
            return source_executor
        
        settings: SourceExecutorSettings = source_executor or self._default_settings
        return self._source_executor_manager.get_or_create(settings)