from enum import Enum, auto
from types import MappingProxyType
from pydantic import BaseModel, ConfigDict, Field

from templisafe.source import *

class SourceLatencyProfile(Enum):
    """Latency profile of a source."""
    NONE = auto()
    LOW = auto()
    HIGH = auto()
    
_SOURCE_LATENCY_MAP: MappingProxyType[type[Source], SourceLatencyProfile] = MappingProxyType({
    InlineSource: SourceLatencyProfile.NONE,
    LocalSource: SourceLatencyProfile.LOW,
    HttpSource: SourceLatencyProfile.HIGH,
    AwsS3BucketSource: SourceLatencyProfile.HIGH,
    AwsSecretsManagerSource: SourceLatencyProfile.HIGH,
    AwsSsmParameterSource: SourceLatencyProfile.HIGH,
    AwsDynamoDBSource: SourceLatencyProfile.HIGH,
})

class StrategyOptimizerSettings(BaseModel):
    """Settings class for defining optimizers for source executor strategies."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        arbitrary_types_allowed=True
    )

    source_latency_map: MappingProxyType[type[Source], SourceLatencyProfile] = Field(
        default_factory=lambda : _SOURCE_LATENCY_MAP,
        description="Map which assign a latency profile to each source kind."
    )

    no_latency_weight: int = Field(
        default=0,
        description="The weight of a source with no latency in the strategy calculation."
    )

    low_latency_weight: int = Field(
        default=10,
        description="The weight of a low latency source in the strategy calculation."
    )

    high_latency_weight: int = Field(
        default=50,
        description="The weight of a high latency source in the strategy calculation."
    )

    default_latency_weight: int = Field(
        default=50,
        description="The weight of a source whose latency is unknown (like a custom source) in the strategy calculation."
    )

    threshold: int = Field(
        default=100,
        description="The threshold to overcome or reach for threading."
    )