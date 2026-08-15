import pytest

from templisafe.executor.source_executor import SourceExecutor
from templisafe.executor.source_executor_manager import SourceExecutorManager
from templisafe.executor.source_executor_resolver import SourceExecutorResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source_executor_settings import (
    SourceExecutorSettings,
    SourceExecutorStrategy,
)


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def default_settings() -> SourceExecutorSettings:
    """Return default SourceExecutorSettings."""
    return SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL, n_threads=1)


@pytest.fixture
def manager(default_settings) -> SourceExecutorManager:
    """SourceExecutorManager with caching enabled."""
    return SourceExecutorManager(settings=ManagerSettings(cache=True))


@pytest.fixture
def resolver(manager, default_settings) -> SourceExecutorResolver:
    """SourceExecutorResolver with default settings."""
    return SourceExecutorResolver(default_settings=default_settings, source_executor_manager=manager)


@pytest.fixture
def executor(manager, default_settings) -> SourceExecutor:
    """Return a SourceExecutor created by the manager."""
    return manager.get_or_create(default_settings)


# -----------------------------
# Tests
# -----------------------------
def test_resolve_already_executor(resolver: SourceExecutorResolver, executor: SourceExecutor):
    """If input is already a SourceExecutor, it is returned as-is."""
    resolved = resolver.resolve(executor)
    assert resolved is executor


def test_resolve_from_settings(resolver: SourceExecutorResolver, manager):
    """If input is SourceExecutorSettings, a new executor is created."""
    new_settings = SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL, n_threads=2)
    resolved = resolver.resolve(new_settings)
    assert isinstance(resolved, SourceExecutor)
    # Should be cached in manager
    resolved2 = manager.get_or_create(new_settings)
    assert resolved is resolved2


def test_resolve_default_settings(resolver: SourceExecutorResolver, default_settings: SourceExecutorSettings):
    """If input is None, resolver returns an executor using default settings."""
    resolved = resolver.resolve()
    assert isinstance(resolved, SourceExecutor)
    assert resolved._settings == default_settings


def test_resolve_multiple_settings(resolver: SourceExecutorResolver):
    """Resolver can create executors for different settings independently."""
    settings1 = SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL, n_threads=1)
    settings2 = SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL, n_threads=2)

    exec1 = resolver.resolve(settings1)
    exec2 = resolver.resolve(settings2)

    assert isinstance(exec1, SourceExecutor)
    assert isinstance(exec2, SourceExecutor)
    assert exec1 is not exec2
    assert exec1._settings != exec2._settings
