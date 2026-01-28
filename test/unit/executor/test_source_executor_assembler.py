import pytest

from templisafe.executor.source_executor_assembler import SourceExecutorAssembler, _DEFAULT_EXECUTOR_SETTINGS
from templisafe.executor.source_executor_resolver import SourceExecutorResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source_executor_settings import (
    SourceExecutorSettings, 
    SourceExecutorStrategy, 
    StopSettings, 
    TenacitySettings,
    WaitSettings
)
from templisafe.executor.source_executor_manager import SourceExecutorManager
from templisafe.executor.retrying_factory import RetryingFactory
from templisafe.util import DEFAULT_MANAGER_SETTINGS


# -----------------------------
# Tests
# -----------------------------
def test_assemble_with_defaults():
    assembler = SourceExecutorAssembler()
    resolver: SourceExecutorResolver = assembler.assemble()

    assert isinstance(resolver, SourceExecutorResolver)
    assert isinstance(resolver._source_executor_manager, SourceExecutorManager)
    assert resolver._source_executor_manager._settings == DEFAULT_MANAGER_SETTINGS
    assert resolver._default_settings == _DEFAULT_EXECUTOR_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = SourceExecutorAssembler()
    manager_settings = ManagerSettings(cache=False)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, SourceExecutorResolver)
    assert resolver._source_executor_manager._settings == manager_settings


def test_assemble_with_custom_executor_settings():
    assembler = SourceExecutorAssembler()
    custom_settings = SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL, n_threads=1)
    resolver = assembler.assemble(default_executor_settings=custom_settings)

    assert resolver._default_settings == custom_settings


def test_assemble_with_all_custom_settings():
    assembler = SourceExecutorAssembler()
    manager_settings = ManagerSettings(cache=False)
    custom_executor_settings = SourceExecutorSettings(
        strategy=SourceExecutorStrategy.SEQUENTIAL, 
        n_threads=2,
        resilience_policy=TenacitySettings(
            stop=StopSettings(max_delay_seconds=12),
            wait=WaitSettings(fixed_seconds=1, jitter=0.5)
        )
    )

    resolver = assembler.assemble(
        manager_settings=manager_settings,
        default_executor_settings=custom_executor_settings,
    )

    assert isinstance(resolver, SourceExecutorResolver)
    assert resolver._source_executor_manager._settings == manager_settings
    assert resolver._default_settings == custom_executor_settings
