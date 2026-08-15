from enum import Enum, auto
from types import MappingProxyType

import pytest

from templisafe.executor.source_executor import SourceRequest
from templisafe.settings.source_strategy_optimizer_settings import (
    _SOURCE_LATENCY_MAP,
    SourceLatencyProfile,
    StrategyOptimizerSettings,
)
from templisafe.source import *


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def default_settings():
    return StrategyOptimizerSettings()


@pytest.fixture
def custom_settings():
    custom_map = MappingProxyType(
        {
            InlineSource: SourceLatencyProfile.NONE,
            LocalSource: SourceLatencyProfile.LOW,
            HttpSource: SourceLatencyProfile.HIGH,
        }
    )
    return StrategyOptimizerSettings(
        source_latency_map=custom_map,
        no_latency_weight=1,
        low_latency_weight=5,
        high_latency_weight=100,
        default_latency_weight=80,
        threshold=50,
    )


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
def test_default_weights(default_settings: StrategyOptimizerSettings):
    assert default_settings.no_latency_weight == 0
    assert default_settings.low_latency_weight == 10
    assert default_settings.high_latency_weight == 50
    assert default_settings.default_latency_weight == 50
    assert default_settings.threshold == 100
    assert isinstance(default_settings.source_latency_map, MappingProxyType)
    assert InlineSource in default_settings.source_latency_map
    assert LocalSource in default_settings.source_latency_map
    assert HttpSource in default_settings.source_latency_map


def test_custom_weights(custom_settings: StrategyOptimizerSettings):
    assert custom_settings.no_latency_weight == 1
    assert custom_settings.low_latency_weight == 5
    assert custom_settings.high_latency_weight == 100
    assert custom_settings.default_latency_weight == 80
    assert custom_settings.threshold == 50
    assert isinstance(custom_settings.source_latency_map, MappingProxyType)
    assert InlineSource in custom_settings.source_latency_map
    assert LocalSource in custom_settings.source_latency_map
    assert HttpSource in custom_settings.source_latency_map


# ---------------------------------------------------------------------------
# SourceLatencyProfile mapping
# ---------------------------------------------------------------------------
def test_source_latency_map_profiles(default_settings: StrategyOptimizerSettings):
    mapping = default_settings.source_latency_map
    assert mapping[InlineSource] == SourceLatencyProfile.NONE
    assert mapping[LocalSource] == SourceLatencyProfile.LOW
    assert mapping[HttpSource] == SourceLatencyProfile.HIGH
    assert mapping[AwsS3BucketSource] == SourceLatencyProfile.HIGH
    assert mapping[AwsSecretsManagerSource] == SourceLatencyProfile.HIGH
    assert mapping[AwsSsmParameterSource] == SourceLatencyProfile.HIGH
    assert mapping[AwsDynamoDBSource] == SourceLatencyProfile.HIGH


# ---------------------------------------------------------------------------
# Overriding defaults
# ---------------------------------------------------------------------------
def test_override_threshold_and_weights():
    settings = StrategyOptimizerSettings(
        no_latency_weight=5,
        low_latency_weight=15,
        high_latency_weight=25,
        default_latency_weight=25,
        threshold=42,
    )
    assert settings.no_latency_weight == 5
    assert settings.low_latency_weight == 15
    assert settings.high_latency_weight == 25
    assert settings.high_latency_weight == 25
    assert settings.threshold == 42


# ---------------------------------------------------------------------------
# Immutability check
# ---------------------------------------------------------------------------
def test_source_latency_map_is_immutable(default_settings: StrategyOptimizerSettings):
    mapping = default_settings.source_latency_map
    with pytest.raises(TypeError):
        mapping[InlineSource] = SourceLatencyProfile.HIGH  # type: ignore
