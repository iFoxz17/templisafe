import time
import pytest
from tenacity import RetryError
from templisafe.executor.retrying_factory import RetryingFactory
from templisafe.executor.source_executor import (
    SourceExecutorRequest, SourceRequest, SourceExecutorResult
)
from templisafe.executor.thread_pool_source_executor import ThreadPoolSourceExecutor
from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_executor_settings import RetryConditionSettings, SourceExecutorSettings, StopSettings, TenacitySettings, WaitSettings
from templisafe.content.content import ContentType
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.source.source import Source

# -----------------------------
# Fixtures
# -----------------------------

MAX_ATTEMPTS: int = 3
DELAY: float = 0.5
EPSILON: float = 0.2
CONTENTS: list[str] = ["Hello", "World", "!", "I", "am", "Mattia"]
MAX_WAIT = 0.2

@pytest.fixture
def default_tenacity_settings():
    return TenacitySettings(
        stop=StopSettings(max_attempts=MAX_ATTEMPTS),
        wait=WaitSettings(fixed_seconds=0.1, jitter=0.1),
        retry_conditions=RetryConditionSettings(retry_if_result_none=True),
        reraise=True
    )

@pytest.fixture
def retrying_factory():
    return RetryingFactory()

@pytest.fixture
def executor(retrying_factory: RetryingFactory, default_tenacity_settings: TenacitySettings):
    settings = SourceExecutorSettings(
        resilience_policy=TenacitySettings(
            stop=StopSettings(max_attempts=5),
            retry_conditions=RetryConditionSettings(retry_if_result_none=True)
        )
    )
    retrying = retrying_factory.create(default_tenacity_settings)
    
    return ThreadPoolSourceExecutor(settings=settings, retrying=retrying)

class SlowSource(Source):
    def __init__(self, settings: InlineSourceSettings, delay: float = DELAY) -> None:
        super().__init__(settings)
        self.delay = delay

    def read(self) -> str:
        time.sleep(self.delay)
        assert isinstance(self._settings, InlineSourceSettings)
        return self._settings.content

@pytest.fixture
def requests():
    return [
        SourceRequest(
            id=str(i),
            source=SlowSource(
                settings=InlineSourceSettings(
                    content_type=ContentType.TEXT,
                    content=content
                )
            )
        )
        for i, content in enumerate(CONTENTS)
    ]
       

# -----------------------------
# Base case
# -----------------------------

def test_execute_sources_concurrently(executor: ThreadPoolSourceExecutor, requests):
    request = SourceExecutorRequest(requests=requests)

    start = time.perf_counter()
    result: SourceExecutorResult = executor.execute(request)
    end = time.perf_counter()
    
    elapsed_s = end - start
    assert elapsed_s < DELAY + EPSILON, "Sources were not executed concurrently"

    assert len(result.results) == len(CONTENTS)
    for i, content in enumerate(CONTENTS):
        assert result.results[i].id == str(i)
        assert result.results[i].content.payload == content
        assert result.results[i].content.type_ == ContentType.TEXT


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

def test_execute_with_source_raising_recovers(executor: ThreadPoolSourceExecutor, requests: list):
    source = RaisingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Recovered"),
    )
    requests.insert(2, SourceRequest(id="fail", source=source))    
    execution_request = SourceExecutorRequest(requests)

    start = time.perf_counter() 
    result: SourceExecutorResult = executor.execute(execution_request)
    end = time.perf_counter()
    
    elapsed_s = end - start
    assert elapsed_s < DELAY + EPSILON + MAX_WAIT * (MAX_ATTEMPTS - 1), "Sources were not executed concurrently"
    

    # --- Verify result was eventually recovered ---
    assert len(result.results) == 7
    r = result.results[2]
    assert r.id == "fail"
    assert r.content.payload == "Recovered"
    assert r.content.type_ == ContentType.TEXT


def test_execute_with_source_raising_fails(executor: ThreadPoolSourceExecutor):
    source = RaisingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Failed"),
        fail_count=MAX_ATTEMPTS
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
            return None         # type: ignore
        assert isinstance(self._settings, InlineSourceSettings)
        return self._settings.content

def test_execute_with_source_returning_none_recovers(executor: ThreadPoolSourceExecutor):
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

def test_execute_with_source_returning_none_fails(executor: ThreadPoolSourceExecutor):
    source = FailingInlineSource(
        InlineSourceSettings(content_type=ContentType.TEXT, content="Failed"),
        fail_count=MAX_ATTEMPTS
    )
    request = SourceExecutorRequest(requests=[SourceRequest(id="fail", source=source)])
    with pytest.raises(RetryError):
        executor.execute(request)