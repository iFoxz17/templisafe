import pytest
from tenacity import RetryError

from templisafe.content.content import ContentType
from templisafe.executor.retrying_factory import RetryingFactory
from templisafe.executor.sequential_source_executor import SequentialSourceExecutor
from templisafe.executor.source_executor import (
    SourceExecutorRequest,
    SourceExecutorResult,
    SourceRequest,
)
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.settings.source_executor_settings import (
    RetryConditionSettings,
    SourceExecutorSettings,
    StopSettings,
    TenacitySettings,
    WaitSettings,
)
from templisafe.source.inline_source import InlineSource

# -----------------------------
# Fixtures
# -----------------------------

MAX_ATTEMPTS: int = 3


@pytest.fixture
def default_tenacity_settings():
    return TenacitySettings(
        stop=StopSettings(max_attempts=MAX_ATTEMPTS),
        wait=WaitSettings(fixed_seconds=0.1, jitter=0.1),
        retry_conditions=RetryConditionSettings(retry_if_result_none=True),
        reraise=True,
    )


@pytest.fixture
def retrying_factory():
    return RetryingFactory()


@pytest.fixture
def executor(retrying_factory: RetryingFactory, default_tenacity_settings: TenacitySettings):
    settings = SourceExecutorSettings(
        resilience_policy=TenacitySettings(
            stop=StopSettings(max_attempts=5),
            retry_conditions=RetryConditionSettings(retry_if_result_none=True),
        )
    )
    retrying = retrying_factory.create(default_tenacity_settings)

    return SequentialSourceExecutor(settings=settings, retrying=retrying)


@pytest.fixture
def inline_sources():
    return [
        SourceRequest(
            id="1",
            source=InlineSource(settings=InlineSourceSettings(content_type=ContentType.TEXT, content="Hello")),
        ),
        SourceRequest(
            id="2",
            source=InlineSource(settings=InlineSourceSettings(content_type=ContentType.TEXT, content="World")),
        ),
        SourceRequest(
            id="3",
            source=InlineSource(settings=InlineSourceSettings(content_type=ContentType.TEXT, content="!")),
        ),
    ]


# -----------------------------
# Base case
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


# -----------------------------
# Raising source
# -----------------------------


class RaisingInlineSource(InlineSource):
    def __init__(self, settings: InlineSourceSettings, fail_count: int = MAX_ATTEMPTS - 1) -> None:
        super().__init__(settings)
        self._fail_count = fail_count

    def read(self) -> str:
        if self._fail_count > 0:
            self._fail_count -= 1
            raise RuntimeError("Simulated read failure")
        assert isinstance(self._settings, InlineSourceSettings)
        return self._settings.content


def test_execute_with_source_raising_recovers(executor: SequentialSourceExecutor):
    source = RaisingInlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="Recovered"))
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    result: SourceExecutorResult = executor.execute(request)

    # --- Verify result was eventually recovered ---
    assert len(result.results) == 1
    r = result.results[0]
    assert r.id == "fail"
    assert r.content.payload == "Recovered"
    assert r.content.type_ == ContentType.TEXT


def test_execute_with_source_raising_fails(executor: SequentialSourceExecutor):
    source = RaisingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Failed"),
        fail_count=MAX_ATTEMPTS,
    )
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    with pytest.raises(RuntimeError):
        executor.execute(request)


# -----------------------------
# Source returning None
# -----------------------------


class FailingInlineSource(InlineSource):
    def __init__(self, settings: InlineSourceSettings, fail_count: int = MAX_ATTEMPTS - 1) -> None:
        super().__init__(settings)
        self._fail_count = fail_count

    def read(self) -> str:
        if self._fail_count > 0:
            self._fail_count -= 1
            return None  # type: ignore
        assert isinstance(self._settings, InlineSourceSettings)
        return self._settings.content


def test_execute_with_source_returning_none_recovers(
    executor: SequentialSourceExecutor,
):
    source = FailingInlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="Recovered"))
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    result: SourceExecutorResult = executor.execute(request)

    # --- Verify result was eventually recovered ---
    assert len(result.results) == 1
    r = result.results[0]
    assert r.id == "fail"
    assert r.content.payload == "Recovered"
    assert r.content.type_ == ContentType.TEXT


def test_execute_with_source_returning_none_fails(executor: SequentialSourceExecutor):
    source = FailingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Failed"),
        fail_count=MAX_ATTEMPTS,
    )
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    with pytest.raises(RetryError):
        executor.execute(request)
