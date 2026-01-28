from typing import Any
import pytest
from tenacity import Retrying, RetryError
from time import monotonic, sleep

from templisafe.settings.source_executor_settings import (
    StopSettings,
    WaitSettings,
    RetryConditionSettings,
    TenacitySettings,
)
from templisafe.executor.retrying_factory import RetryingFactory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def factory() -> RetryingFactory:
    return RetryingFactory()


@pytest.fixture
def default_policy() -> TenacitySettings:
    return TenacitySettings()


@pytest.fixture
def retry_on_none_policy() -> TenacitySettings:
    return TenacitySettings(
        retry_conditions=RetryConditionSettings(retry_if_result_none=True),
        stop=StopSettings(max_attempts=3),
        wait=WaitSettings(fixed_seconds=0.0),
        reraise=False,
    )


@pytest.fixture
def retry_on_exception_policy() -> TenacitySettings:
    return TenacitySettings(
        stop=StopSettings(max_attempts=3),
        wait=WaitSettings(fixed_seconds=0.0),
        reraise=False,
    )


@pytest.fixture
def retry_exhaust_policy() -> TenacitySettings:
    return TenacitySettings(
        stop=StopSettings(max_attempts=2),
        wait=WaitSettings(fixed_seconds=0.0),
        reraise=True,
    )


# ---------------------------------------------------------------------------
# Factory creation
# ---------------------------------------------------------------------------

def test_factory_create_returns_retrying(factory: RetryingFactory, default_policy):
    retrying = factory.create(default_policy)
    assert isinstance(retrying, Retrying)


def test_factory_create_with_defaults(factory: RetryingFactory):
    retrying = factory.create(TenacitySettings())
    assert isinstance(retrying, Retrying)


# ---------------------------------------------------------------------------
# Stop policy behavior
# ---------------------------------------------------------------------------

def test_stop_after_max_attempts(factory: RetryingFactory, retry_on_exception_policy):
    retrying = factory.create(retry_on_exception_policy)

    calls = {"count": 0}

    def always_fail():
        calls["count"] += 1
        raise ValueError("boom")

    # Should not raise because reraise=False
    with pytest.raises(RetryError):
        _ = retrying(always_fail)
    

    # Max attempts is 3 → initial + 2 retries
    assert calls["count"] == 3


# ---------------------------------------------------------------------------
# Retry on result=None
# ---------------------------------------------------------------------------

def test_retry_on_none_result(factory: RetryingFactory, retry_on_none_policy):
    retrying = factory.create(retry_on_none_policy)
    calls = {"count": 0}

    def sometimes_none():
        calls["count"] += 1
        if calls["count"] < 3:
            return None
        return "ok"

    result = retrying(sometimes_none)

    assert result == "ok"
    assert calls["count"] == 3


# ---------------------------------------------------------------------------
# Retry on exception
# ---------------------------------------------------------------------------

def test_retry_on_exception(factory: RetryingFactory, retry_on_exception_policy):
    retrying = factory.create(retry_on_exception_policy)
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise ValueError("fail")
        return "success"

    result = retrying(flaky)
    assert result == "success"
    assert calls["count"] == 3


# ---------------------------------------------------------------------------
# Exhausted retries with reraise
# ---------------------------------------------------------------------------

def test_retry_exhaustion_reraises(factory: RetryingFactory, retry_exhaust_policy):
    retrying = factory.create(retry_exhaust_policy)

    def always_fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        retrying(always_fail)


# ---------------------------------------------------------------------------
# Combined wait strategy test
# ---------------------------------------------------------------------------

def test_combined_wait_strategy(factory: RetryingFactory):
    """
    Test that multiple wait strategies are combined correctly using wait_chain:
    fixed wait + exponential wait + jitter.
    """
    policy = TenacitySettings(
        stop=StopSettings(max_attempts=3),
        wait=WaitSettings(
            fixed_seconds=0.05,
            multiplier_seconds=0.1,
            exponential_base=2.0,
            max_seconds=0.2,
            jitter=0.02
        ),
        reraise=False
    )

    retrying: Retrying = factory.create(policy)

    calls: dict[str, Any] = {"count": 0, "times": []}

    def flaky():
        calls["count"] += 1
        calls["times"].append(monotonic())
        if calls["count"] < 3:
            raise ValueError("fail")
        return "ok"

    start = monotonic()
    result = retrying(flaky)
    end = monotonic()

    # Verify the function eventually returns successfully
    assert result == "ok"
    assert calls["count"] == 3

    # Verify some minimal time passed due to waits
    total_wait_time = end - start
    # The sum of fixed + exp waits should be at least 0.05
    assert total_wait_time >= 0.05
    assert total_wait_time < 1.0  # sanity check, not too long

    # Ensure the calls times are strictly increasing
    times = calls["times"]
    assert all(t2 > t1 for t1, t2 in zip(times, times[1:]))
