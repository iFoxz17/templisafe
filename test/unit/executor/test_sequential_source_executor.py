from multiprocessing import Value
import pytest
from templisafe.content.content import Content
from templisafe.executor.source_executor import (
    SourceExecutorRequest, SourceRequest, SourceExecutorResult
)
from templisafe.executor.sequential_source_executor import SequentialSourceExecutor
from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_executor_settings import RetryConditionSettings, SourceExecutorSettings, StopSettings, TenacitySettings
from templisafe.content.content import ContentType
from templisafe.settings.source.inline_source_settings import InlineSourceSettings

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def executor():
    settings = SourceExecutorSettings(
        resilience_policy=TenacitySettings(
            stop=StopSettings(max_attempts=5),
            retry_conditions=RetryConditionSettings(retry_if_result_none=True)
        )
    )
    return SequentialSourceExecutor(settings=settings)

@pytest.fixture
def inline_sources():
    return [
        SourceRequest(
            id="1",
            source=InlineSource(
                settings=InlineSourceSettings(
                    content_type=ContentType.TEXT,
                    content="Hello"
                )
            )
        ),
        SourceRequest(
            id="2",
            source=InlineSource(
                settings=InlineSourceSettings(
                    content_type=ContentType.TEXT,
                    content="World"
                )
            )
        ),
        SourceRequest(
            id="3",
            source=InlineSource(
                settings=InlineSourceSettings(
                    content_type=ContentType.TEXT,
                    content="!"
                )
            )
        ),
    ]

# -----------------------------
# Tests
# -----------------------------
def test_execute_sources_sequential(executor: SequentialSourceExecutor, inline_sources):
    request = SourceExecutorRequest(requests=inline_sources)
    result: SourceExecutorResult = executor.execute(request)

    assert len(result.results) == 3
    assert result.results[0].id == "1"
    assert result.results[0].content.payload == "Hello"
    assert result.results[0].content.type_ == ContentType.TEXT

    assert result.results[1].id == "2"
    assert result.results[1].content.payload == "World"
    assert result.results[1].content.type_ == ContentType.TEXT

    assert result.results[2].id == "3"
    assert result.results[2].content.payload == "!"
    assert result.results[2].content.type_ == ContentType.TEXT

def test_execute_source_raises_sequential_with_retry(executor: SequentialSourceExecutor):
    
    # --- Patch a source to fail the first two reads ---
    class FailingInlineSource(InlineSource):
        def __init__(self, settings: InlineSourceSettings, fail_count: int = 2) -> None:
            super().__init__(settings)
            self._fail_count = fail_count

        def read(self) -> str:
            if self._fail_count > 0:
                self._fail_count -= 1
                raise ValueError("Simulated read failure")
            assert isinstance(self._settings, InlineSourceSettings)
            return self._settings.content

    source = FailingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Recovered")
    )
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    result: SourceExecutorResult = executor.execute(request)

    # --- Verify result was eventually recovered ---
    assert len(result.results) == 1
    r = result.results[0]
    assert r.id == "fail"
    assert r.content.payload == "Recovered"
    assert r.content.type_ == ContentType.TEXT

def test_execute_source_returns_none_sequential_with_retry(executor: SequentialSourceExecutor):
    
    # --- Patch a source to fail the first two reads ---
    class FailingInlineSource(InlineSource):
        def __init__(self, settings: InlineSourceSettings, fail_count: int = 2) -> None:
            super().__init__(settings)
            self._fail_count = fail_count

        def read(self) -> str:
            if self._fail_count > 0:
                self._fail_count -= 1
                return None         # type: ignore
            assert isinstance(self._settings, InlineSourceSettings)
            return self._settings.content

    source = FailingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Recovered")
    )
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    result: SourceExecutorResult = executor.execute(request)

    # --- Verify result was eventually recovered ---
    assert len(result.results) == 1
    r = result.results[0]
    assert r.id == "fail"
    assert r.content.payload == "Recovered"
    assert r.content.type_ == ContentType.TEXT