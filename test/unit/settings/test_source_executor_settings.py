from typing import Any
import pytest
from pydantic import ValidationError

from templisafe.settings.source_executor_settings import (
    StopSettings,
    WaitSettings,
    RetryConditionSettings,
    TenacitySettings,
    SourceExecutorSettings,
    SourceExecutorStrategy,
)

# ---------------------------------------------------------------------------
# Sample configurations
# ---------------------------------------------------------------------------

STOP_CONFIG = {"max_attempts": 5, "max_delay_seconds": 60.0}
WAIT_CONFIG = {"fixed_seconds": 2.0, "exponential_base": 3.0, "multiplier_seconds": 1.5, "max_seconds": 10.0, "min_seconds": 0.1, "jitter": 0.5}
RETRY_CONFIG = {"retry_if_result_none": True}

TENACITY_CONFIG = {
    "stop": STOP_CONFIG,
    "wait": WAIT_CONFIG,
    "retry_conditions": RETRY_CONFIG,
    "reraise": False,
}

EXECUTOR_CONFIG = {
    "resilience_policy": TENACITY_CONFIG,
    "strategy": "sequential",
    "n_threads": 4
}


# ---------------------------------------------------------------------------
# StopSettings / WaitSettings / RetryConditionSettings tests
# ---------------------------------------------------------------------------

def test_stop_settings_defaults():
    stop = StopSettings()
    assert stop.max_attempts is None
    assert stop.max_delay_seconds is None

def test_stop_settings_from_dict():
    stop = StopSettings.from_dict(STOP_CONFIG)
    assert stop.max_attempts == 5
    assert stop.max_delay_seconds == 60.0

def test_wait_settings_defaults():
    wait = WaitSettings()
    assert wait.fixed_seconds is None
    assert wait.exponential_base is None
    assert wait.multiplier_seconds is None
    assert wait.max_seconds is None
    assert wait.min_seconds is None
    assert wait.jitter is None

def test_wait_settings_from_dict():
    wait = WaitSettings.from_dict(WAIT_CONFIG)
    assert wait.fixed_seconds == 2.0
    assert wait.exponential_base == 3.0
    assert wait.multiplier_seconds == 1.5
    assert wait.max_seconds == 10.0
    assert wait.min_seconds == 0.1
    assert wait.jitter == 0.5

def test_retry_condition_settings_defaults():
    retry = RetryConditionSettings()
    assert retry.retry_if_result_none is False

def test_retry_condition_settings_from_dict():
    retry = RetryConditionSettings.from_dict(RETRY_CONFIG)
    assert retry.retry_if_result_none is True

def test_retry_condition_settings_hashable():
    retry = RetryConditionSettings.from_dict(RETRY_CONFIG)
    cache: set[RetryConditionSettings] = {retry}        # type: ignore
    assert retry in cache

    cache_dict: dict[RetryConditionSettings, Any] = {retry: "hello"}        # type: ignore
    assert retry in cache_dict


# ---------------------------------------------------------------------------
# TenacitySettings tests
# ---------------------------------------------------------------------------

def test_tenacity_settings_defaults():
    tenacity = TenacitySettings()
    assert isinstance(tenacity.stop, StopSettings)
    assert isinstance(tenacity.wait, WaitSettings)
    assert isinstance(tenacity.retry_conditions, RetryConditionSettings)
    assert tenacity.reraise is True

def test_tenacity_settings_from_dict():
    tenacity = TenacitySettings.from_dict(TENACITY_CONFIG)
    assert tenacity.stop.max_attempts == 5
    assert tenacity.wait.fixed_seconds == 2.0
    assert tenacity.reraise is False

def test_tenacity_settings_serialization():
    tenacity = TenacitySettings.from_dict(TENACITY_CONFIG)
    json_str = tenacity.model_dump_json()
    tenacity2 = TenacitySettings.model_validate_json(json_str)
    assert tenacity2.stop.max_attempts == tenacity.stop.max_attempts
    assert tenacity2.wait.fixed_seconds == tenacity.wait.fixed_seconds
    assert tenacity2.retry_conditions.retry_if_result_none == tenacity.retry_conditions.retry_if_result_none

def test_tenacity_settings_hashable():
    tenacity = TenacitySettings.from_dict(TENACITY_CONFIG)
    cache: set[TenacitySettings] = {tenacity}
    assert tenacity in cache

    cache_dict: dict[TenacitySettings, Any] = {tenacity: "hello"}
    assert tenacity in cache_dict

# ---------------------------------------------------------------------------
# SourceExecutorSettings tests
# ---------------------------------------------------------------------------

def test_executor_settings_defaults():
    executor = SourceExecutorSettings()
    assert isinstance(executor.resilience_policy, TenacitySettings)
    assert executor.strategy is None
    assert executor.n_threads is None

def test_executor_settings_from_dict():
    executor = SourceExecutorSettings.from_dict(EXECUTOR_CONFIG)
    assert executor.resilience_policy.stop.max_attempts == 5
    assert executor.strategy == SourceExecutorStrategy.SEQUENTIAL
    assert executor.n_threads == 4

def test_executor_settings_invalid_threads():
    with pytest.raises(ValidationError):
        SourceExecutorSettings(n_threads=0)  # n_threads >= 1

def test_executor_settings_invalid_strategy_type():
    with pytest.raises(ValidationError):
        SourceExecutorSettings(strategy="invalid")  # type: ignore

def test_executor_settings_serialization():
    executor = SourceExecutorSettings.from_dict(EXECUTOR_CONFIG)
    json_str = executor.model_dump_json()
    executor2 = SourceExecutorSettings.model_validate_json(json_str)
    assert executor2.strategy == executor.strategy
    assert executor2.n_threads == executor.n_threads
    assert executor2.resilience_policy.stop.max_attempts == executor.resilience_policy.stop.max_attempts

def test_executor_settings_hashable():
    executor: SourceExecutorSettings = SourceExecutorSettings.from_dict(EXECUTOR_CONFIG)
    cache: set[SourceExecutorSettings] = {executor}
    assert executor in cache

    cache_dict: dict[SourceExecutorSettings, Any] = {executor: "hello"}
    assert executor in cache_dict