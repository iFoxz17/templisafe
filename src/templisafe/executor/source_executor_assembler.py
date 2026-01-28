from templisafe.executor.retrying_factory import RetryingFactory
from templisafe.executor.source_executor_manager import SourceExecutorFactory, SourceExecutorManager
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source_executor_settings import RetryConditionSettings, SourceExecutorSettings, SourceExecutorStrategy, StopSettings, TenacitySettings, WaitSettings
from templisafe.executor.source_executor_resolver import SourceExecutorResolver
from templisafe.util import DEFAULT_MANAGER_SETTINGS

_DEFAULT_EXECUTOR_SETTINGS: SourceExecutorSettings = SourceExecutorSettings(
    strategy=SourceExecutorStrategy.THREAD_POOL,
    n_threads=None,
    resilience_policy=TenacitySettings(
        stop=StopSettings(max_attempts=3, max_delay_seconds=10),
        wait=WaitSettings(exponential_base=2, multiplier_seconds=0.5, max_seconds=5),
        retry_conditions=RetryConditionSettings(retry_if_result_none=True),
        reraise=True
    )
)

class SourceExecutorAssembler:
    """Assembles a `SourceExecutorResolver` with all necessary components."""

    __slots__ : tuple[str, ...] = ()

    def assemble(
            self, 
            manager_settings: ManagerSettings | None = None,
            default_executor_settings: SourceExecutorSettings | None = None
            ) -> SourceExecutorResolver:
        """
        Create and return a fully initialized `SourceExecutorResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_executor_settings : SourceExecutorSettings | None
            Optional executor settings to use as default. If not provided, a default is used.

        Returns
        -------
        SourceExecutorResolver
            A `SourceExecutorResolver` ready to resolve executors.
        """

        retrying_factory: RetryingFactory = RetryingFactory()
        factory: SourceExecutorFactory = SourceExecutorFactory(retrying_factory)
        manager: SourceExecutorManager = SourceExecutorManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS,
            factory=factory
        )
        resolver: SourceExecutorResolver = SourceExecutorResolver(
            source_executor_manager=manager,
            default_settings=(
                default_executor_settings or _DEFAULT_EXECUTOR_SETTINGS
            )
        )

        return resolver
