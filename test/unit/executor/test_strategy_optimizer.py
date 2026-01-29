import pytest
from types import MappingProxyType
import time

from templisafe.executor.source_executor import SourceRequest
from templisafe.settings.source.custom_source_settings import CustomSourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorStrategy
from templisafe.settings.source_strategy_optimizer_settings import (
    StrategyOptimizerSettings,
    SourceLatencyProfile,
)
from templisafe.executor.strategy_optimizer import StrategyOptimizer
from templisafe.source.inline_source import InlineSource
from templisafe.source.local_source import LocalSource
from templisafe.source.http_source import HttpSource
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.settings.source.local_source_settings import LocalSourceSettings
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.content.content import ContentType
from templisafe.source.source import Source

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def custom_settings() -> StrategyOptimizerSettings:
    """Explicit weights for testing independence from defaults."""
    custom_map = MappingProxyType({
        InlineSource: SourceLatencyProfile.NONE,
        LocalSource: SourceLatencyProfile.LOW,
        HttpSource: SourceLatencyProfile.HIGH,
    })
    return StrategyOptimizerSettings(
        source_latency_map=custom_map,
        no_latency_weight=0,
        low_latency_weight=10,
        high_latency_weight=50,
        default_latency_weight=30,
        threshold=50,
    )


@pytest.fixture
def optimizer(custom_settings) -> StrategyOptimizer:
    return StrategyOptimizer(custom_settings)


@pytest.fixture
def sources_inline() -> list[Source]:
    """Two inline sources (no latency)."""
    return [
        InlineSource(
            settings=InlineSourceSettings(
                content_type=ContentType.TEXT,
                content="Hello"
            )
        ),
        InlineSource(
            settings=InlineSourceSettings(
                content_type=ContentType.TEXT,
                content="World"
            )
        )
    ]


@pytest.fixture
def sources_mixed() -> list[Source]:
    """Mixed sources: inline, local, high latency (HTTP)."""
    return [
        InlineSource(
            settings=InlineSourceSettings(
                content_type=ContentType.TEXT,
                content="A"
            )
        ),
        LocalSource(
            settings=LocalSourceSettings(
                content_type=ContentType.TEXT,
                path="/tmp/file.txt"
            )
        ),
        HttpSource(
            settings=HttpSourceSettings(
                content_type=ContentType.TEXT,
                url="http://example.com"
            )
        ),
    ]


@pytest.fixture
def sources_many_local() -> list[Source]:
    """Many low latency sources to test threshold break."""
    return [
        LocalSource(LocalSourceSettings(content_type=ContentType.TEXT, path=f"/tmp/file{i}.txt"))
        for i in range(500_000)
    ]


# -----------------------------
# Tests
# -----------------------------
def test_source_weights_explicit(optimizer: StrategyOptimizer):
    """Verify that explicit weights are correctly applied."""
    assert optimizer._source_weight(InlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="x"))) == 0
    assert optimizer._source_weight(LocalSource(LocalSourceSettings(content_type=ContentType.TEXT, path="/tmp/x"))) == 10
    assert optimizer._source_weight(HttpSource(HttpSourceSettings(content_type=ContentType.TEXT, url="http://x"))) == 50

def test_custom_source_weights_explicit(optimizer: StrategyOptimizer):
    """Verify that explicit weights are correctly applied."""
    class MySource(Source):
        def read(self) -> str:
            return "Hello world"

    assert optimizer._source_weight(MySource(CustomSourceSettings(content_type=ContentType.TEXT, context={}))) == 30
    
def test_strategy_sequential_for_inline_only(optimizer: StrategyOptimizer, sources_inline):
    """Total weight below threshold → SEQUENTIAL."""
    strat = optimizer.strategy(sources_inline)
    assert strat == SourceExecutorStrategy.SEQUENTIAL


def test_strategy_thread_pool_for_mixed_sources(optimizer: StrategyOptimizer, sources_mixed):
    """Mixed sources with at least one high-latency should reach threshold → THREAD_POOL."""
    strat = optimizer.strategy(sources_mixed)
    # weights: 0 + 10 + 50 = 60 > threshold=50 → THREAD_POOL
    assert strat == SourceExecutorStrategy.THREAD_POOL


def test_strategy_thread_pool_for_many_local_sources(optimizer: StrategyOptimizer, sources_many_local):
    """Many low-latency sources should sum to threshold → THREAD_POOL.
    Check that the loop exits early (break is effective) by measuring execution time.
    """
    start = time.perf_counter()
    strat = optimizer.strategy(sources_many_local)
    end = time.perf_counter()

    # Assert strategy
    assert strat == SourceExecutorStrategy.THREAD_POOL

    # Assert execution time is very small (loop breaks early)
    elapsed_ms = (end - start) * 1000
    # Expect it to be under 10 ms even with 500_000 sources if early return works
    assert elapsed_ms < 10, f"Loop did not break early, took {elapsed_ms:.2f} ms"
