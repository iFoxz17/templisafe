import pytest
from tenacity import Retrying

from templisafe.exceptions.source_executor_error import UnsupportedExecutorStrategy
from templisafe.executor.retrying_factory import RetryingFactory
from templisafe.executor.sequential_source_executor import SequentialSourceExecutor
from templisafe.executor.source_executor_manager import (
    SourceExecutorFactory,
    SourceExecutorManager,
)
from templisafe.executor.thread_pool_source_executor import ThreadPoolSourceExecutor
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source_executor_settings import (
    SourceExecutorSettings,
    SourceExecutorStrategy,
    TenacitySettings,
)

# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def factory() -> SourceExecutorFactory:
    """Return a SourceExecutorFactory instance."""
    return SourceExecutorFactory()


@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def manager(request) -> SourceExecutorManager:
    """Return a SourceExecutorManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return SourceExecutorManager(settings=settings)


@pytest.fixture
def executor_settings_sequential() -> SourceExecutorSettings:
    """Return SourceExecutorSettings for sequential execution."""
    return SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL)


@pytest.fixture
def executor_settings_thread_pool() -> SourceExecutorSettings:
    """Return SourceExecutorSettings for thread pool execution."""
    return SourceExecutorSettings(strategy=SourceExecutorStrategy.THREAD_POOL)


# -----------------------------
# SourceExecutorFactory tests
# -----------------------------


def test_factory_creates_sequential_executor(
    factory: SourceExecutorFactory, executor_settings_sequential: SourceExecutorSettings
):
    """Factory returns a SequentialSourceExecutor with proper retrying object."""
    executor = factory.create(executor_settings_sequential)
    assert isinstance(executor, SequentialSourceExecutor)
    assert hasattr(executor, "_retrying")
    assert isinstance(executor._retrying, Retrying)


def test_factory_creates_thread_pool_executor(
    factory: SourceExecutorFactory,
    executor_settings_thread_pool: SourceExecutorSettings,
):
    """Factory returns a ThreadPoolSourceExecutor with proper retrying object."""
    executor = factory.create(executor_settings_thread_pool)
    assert isinstance(executor, ThreadPoolSourceExecutor)
    assert hasattr(executor, "_retrying")
    assert isinstance(executor._retrying, Retrying)


'''
def test_factory_unsupported_strategy_raises(factory: SourceExecutorFactory):
    """Factory raises UnsupportedExecutorStrategy for invalid strategy."""
    settings = SourceExecutorSettings(strategy="Unknown strategy")  # type: ignore
    with pytest.raises(Exception):
        factory.create(settings)
'''

# -----------------------------
# SourceExecutorManager tests
# -----------------------------


def test_manager_get_or_create(manager: SourceExecutorManager, executor_settings_sequential: SourceExecutorSettings):
    """Manager returns executor instances and respects caching."""
    executor1 = manager.get_or_create(executor_settings_sequential)
    executor2 = manager.get_or_create(executor_settings_sequential)

    # Always returns correct type
    assert isinstance(executor1, SequentialSourceExecutor)
    assert isinstance(executor2, SequentialSourceExecutor)

    if manager._settings.cache:
        # Should be the same instance if caching enabled
        assert executor1 is executor2
        assert executor_settings_sequential in manager
    else:
        # Should be different instances if caching disabled
        assert executor1 is not executor2
        assert executor_settings_sequential not in manager


def test_manager_get_or_create_thread_pool(
    manager: SourceExecutorManager,
    executor_settings_thread_pool: SourceExecutorSettings,
):
    """Manager returns ThreadPoolSourceExecutor correctly and respects caching."""
    executor = manager.get_or_create(executor_settings_thread_pool)
    assert isinstance(executor, ThreadPoolSourceExecutor)

    if manager._settings.cache:
        # Should be cached
        assert executor_settings_thread_pool in manager
    else:
        assert executor_settings_thread_pool not in manager


def test_manager_contains_only_cached_executors(
    manager: SourceExecutorManager, executor_settings_sequential: SourceExecutorSettings
):
    """__contains__ reflects only cached executors."""
    # Initially nothing cached
    assert executor_settings_sequential not in manager

    _ = manager.get_or_create(executor_settings_sequential)

    if manager._settings.cache:
        assert executor_settings_sequential in manager
    else:
        assert executor_settings_sequential not in manager
