import pytest
from unittest.mock import Mock

from templisafe.content.content import Content, ContentType
from templisafe.executor.source_executor import SourceExecutor, SourceExecutorResult, SourceResult
from templisafe.executor.source_executor_resolver import SourceExecutorResolver
from templisafe.executor.strategy_optimizer import StrategyOptimizer
from templisafe.settings.source_executor_settings import SourceExecutorSettings, SourceExecutorStrategy
from templisafe.source.source import Source
from templisafe.provider.content_provider import ContentProvider, SourceGroup, ContentGroup


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def mock_executor() -> SourceExecutor:
    """Return a mock SourceExecutor."""
    executor = Mock(spec=SourceExecutor)
    def execute(request):
        # return SourceExecutorResult with Content for each request
        results = [SourceResult(id=req.id, content=Content(payload=f"content-{req.id}", type_=ContentType.TEXT))
                   for req in request.requests]
        return SourceExecutorResult(results=results)
    executor.execute.side_effect = execute
    return executor

@pytest.fixture
def mock_resolver(mock_executor) -> SourceExecutorResolver:
    """Return a mock resolver that always returns the mock executor."""
    resolver = Mock(spec=SourceExecutorResolver)
    resolver.resolve.side_effect = lambda se: mock_executor if isinstance(se, SourceExecutorSettings) else se
    resolver.default_settings = SourceExecutorSettings(strategy=SourceExecutorStrategy.THREAD_POOL)
    return resolver

@pytest.fixture
def mock_optimizer() -> StrategyOptimizer:
    """Return a mock strategy optimizer that returns a fixed strategy."""
    optimizer = Mock(spec=StrategyOptimizer)
    optimizer.strategy.return_value = SourceExecutorStrategy.THREAD_POOL
    return optimizer

@pytest.fixture
def provider(mock_resolver, mock_optimizer) -> ContentProvider:
    """Return a ContentProvider instance with mocks."""
    return ContentProvider(mock_resolver, mock_optimizer)

@pytest.fixture
def source_group() -> SourceGroup:
    """Return a simple SourceGroup with multiple mock Sources."""
    sources = {str(i): Mock(spec=Source) for i in range(3)}
    return SourceGroup(sources=sources)       # type: ignore


# -----------------------------
# Tests
# -----------------------------

def test_provide_with_default_settings(provider: ContentProvider, source_group: SourceGroup):
    """Provide resolves content using default executor settings."""
    content_group: ContentGroup = provider.provide(source_group)
    assert isinstance(content_group, ContentGroup)
    assert set(content_group.contents.keys()) == set(source_group.sources.keys())
    for key, content in content_group.contents.items():
        assert content.payload == f"content-{key}"
        assert content.type_ == ContentType.TEXT
    # The optimizer should have been called because default settings always optimize
    provider._strategy_optimizer.strategy.assert_called_once()       # type: ignore

def test_provide_with_custom_settings_without_strategy(provider: ContentProvider, source_group: SourceGroup):
    """If custom settings lack strategy, the optimizer is called."""
    custom_settings = SourceExecutorSettings(strategy=None)
    provider.provide(source_group, source_executor=custom_settings)
    provider._strategy_optimizer.strategy.assert_called_once()       # type: ignore

def test_provide_with_custom_settings_with_strategy(provider: ContentProvider, source_group: SourceGroup):
    """If custom settings already have a strategy, optimizer is not called."""
    custom_settings = SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL)
    provider.provide(source_group, source_executor=custom_settings)
    provider._strategy_optimizer.strategy.assert_not_called()       # type: ignore

def test_provide_with_executor_instance(provider: ContentProvider, source_group: SourceGroup, mock_executor):
    """If a SourceExecutor instance is passed, it is used directly."""
    content_group = provider.provide(source_group, source_executor=mock_executor)
    assert isinstance(content_group, ContentGroup)
    # Optimizer should not be called when passing executor instance
    provider._strategy_optimizer.strategy.assert_not_called()       # type: ignore
    # Executor execute should be called once
    mock_executor.execute.assert_called_once()
