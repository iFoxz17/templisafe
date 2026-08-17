from enum import Enum
from typing import TypeVar

from pydantic import Field

from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="SourceExecutorSettings")

# ---------------------------------------------------------------------------------------------
# Tenacity settings
# ---------------------------------------------------------------------------------------------


# -----------------------------
# Stop strategies
# -----------------------------
class StopSettings(Settings):
    """Configuration for stop conditions."""

    max_attempts: int | None = Field(default=None, description="Maximum number of attempts before giving up")
    max_delay_seconds: float | None = Field(default=None, description="Maximum total time to keep retrying")


# -----------------------------
# Wait strategies
# -----------------------------
class WaitSettings(Settings):
    """Configuration for wait/backoff between retries."""

    fixed_seconds: float | None = Field(default=None, description="Fixed wait time between retries")
    exponential_base: float | None = Field(default=None, description="Base for exponential backoff")
    multiplier_seconds: float | None = Field(default=None, description="Multiplier for backoff")
    min_seconds: float | None = Field(default=None, description="Minimum wait time")
    max_seconds: float | None = Field(default=None, description="Maximum wait time")
    jitter: float | None = Field(default=None, description="Random jitter to add to wait")


# -----------------------------
# Retry conditions
# -----------------------------
class RetryConditionSettings(Settings):
    """Configuration for retry conditions."""

    # Not serializable
    """
    retry_exceptions: tuple[type[BaseException], ...] | None = Field(
        default=(Exception,), 
        description="Tuple of exception types that trigger a retry"
    )
    """

    retry_if_result_none: bool = Field(default=False, description="Retry if function returns None")


# -----------------------------
# Resilience policy: main Tenacity settings
# -----------------------------
class TenacitySettings(Settings):
    """Main settings for a retryable operation using Tenacity."""

    stop: StopSettings = Field(default_factory=StopSettings, description="The stop policy settings")
    wait: WaitSettings = Field(default_factory=WaitSettings, description="The wait policy settings")
    retry_conditions: RetryConditionSettings = Field(
        default_factory=RetryConditionSettings,
        description="The retry conditions settings",
    )
    reraise: bool = Field(
        default=True,
        description="If True, re-raise the last exception after retries are exhausted",
    )

    def __hash__(self):
        return hash(
            (
                self.stop,
                self.wait,
                self.retry_conditions,
                self.reraise,
            )
        )

    # Not serializable
    """
    before_sleep: Callable[[int, BaseException | None]] | None = Field(
        default=None, description="Callback called before sleeping between retries"
    )
    after_attempt: Callable[[int, BaseException | None]] | None = Field(
        default=None, description="Callback called after each attempt"
    )
    """


# ---------------------------------------------------------------------------------------------
# Source executor settings
# ---------------------------------------------------------------------------------------------


class SourceExecutorStrategy(Enum):
    SEQUENTIAL = "sequential"
    THREAD_POOL = "thread_pool"


class SourceExecutorSettings(Settings):
    """Settings class for defining source executors."""

    resilience_policy: TenacitySettings = Field(
        default_factory=TenacitySettings, description="The resilience policy settings"
    )
    strategy: SourceExecutorStrategy | None = Field(
        default=None,
        description=("The execution strategy. If None, it is automatically selected based on the given sources."),
    )
    n_threads: int | None = Field(
        default=None,
        description=(
            "Max number of threads for the threading execution strategy. "
            "If None, the number of thread is automatically chosen. "
            "If the selected strategy is not threading, this field is ignored"
        ),
        ge=1,
    )

    @property
    def has_strategy(self) -> bool:
        return self.strategy is not None

    @property
    def actual_strategy(self) -> SourceExecutorStrategy:
        if self.strategy is None:
            raise ValueError("Execution strategy not set")
        return self.strategy

    def __hash__(self):
        return hash(
            (
                self.resilience_policy,
                self.strategy,
                self.n_threads,
            )
        )


Settings.register_kind(SettingsKind.SOURCE_EXECUTOR_SETTINGS, SourceExecutorSettings)
