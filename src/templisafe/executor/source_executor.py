from abc import ABC, abstractmethod
from dataclasses import dataclass
from tenacity import (
    Retrying,
    retry_any,
    retry_if_exception_type,
    retry_if_result, 
    stop_after_attempt, 
    stop_after_delay, 
    stop_never, 
    wait_fixed, 
    wait_exponential, 
    wait_random, 
    wait_chain
)

from templisafe.content.content import Content
from templisafe.source.source import Source
from templisafe.settings.source_executor_settings import SourceExecutorSettings, TenacitySettings

#---------------------------------------------------------------------------------------------
# Source request
#---------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SourceRequest:
    id: str
    source: Source

@dataclass(frozen=True, slots=True)
class SourceExecutorRequest:
    requests: list[SourceRequest]
    
    @property
    def requests_dict(self) -> dict[str, SourceRequest]:
        return {r.id: r for r in self.requests}
    
#---------------------------------------------------------------------------------------------
# Source result
#---------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SourceResult:
    id: str
    content: Content

@dataclass(frozen=True, slots=True)
class SourceExecutorResult:
    results: list[SourceResult]
    
    @property
    def results_dict(self) -> dict[str, SourceResult]:
        return {r.id: r for r in self.results}

#---------------------------------------------------------------------------------------------
# Source executor
#---------------------------------------------------------------------------------------------

class SourceExecutor(ABC):
    """Abstract base class for source executors reading the content of sources."""

    __slots__ = ("_settings", "_retrying")

    def __init__(self, settings: SourceExecutorSettings) -> None:
        self._settings: SourceExecutorSettings = settings
        self._retrying: Retrying = self._build_retrying(settings.resilience_policy)

    def _build_retrying(self, policy: TenacitySettings) -> Retrying:
        
        # Stop policy
        stop = (
            stop_after_attempt(policy.stop.max_attempts)
            if policy.stop.max_attempts is not None
            else stop_after_delay(policy.stop.max_delay_seconds)
            if policy.stop.max_delay_seconds is not None
            else stop_never
        )
        
        # Wait policy
        if policy.wait.fixed_seconds is not None:
            wait = wait_fixed(policy.wait.fixed_seconds)
        else:
            kwargs = {
                k: v
                for k, v in zip(
                    ("multiplier", "exp_base", "min", "max", "jitter"),
                    (policy.wait.multiplier_seconds, policy.wait.exponential_base, policy.wait.min_seconds, 
                     policy.wait.max_seconds, policy.wait.jitter
                    )
                )
                if v is not None
            }
            wait = wait_exponential(**kwargs)

        if policy.wait.jitter is not None:
            wait = wait_chain(wait, wait_random(0, policy.wait.jitter))
        
        # Retry condition        
        retry_condition = retry_any(
            retry_if_exception_type(Exception),
            retry_if_result(
                lambda result: policy.retry_conditions.retry_if_result_none and result is None
                )
        )

        return Retrying(
            stop=stop,
            wait=wait,
            retry=retry_condition,
            reraise=policy.reraise
        )
        
    @abstractmethod
    def execute(self, request: SourceExecutorRequest) -> SourceExecutorResult:
        """
        Execute the given request with the set resilience strategy and return the results.
        The order of the requests is preserved in the result. 

        Parameters
        ----------
        request : SourceExecutorRequest
            A request containing multiple sources to be read.

        Returns
        -------
        SourceExecutorResult
            The aggregated results of all source reads, preserving order.

        Raises
        -------
            Source-related exceptions, if the resilience strategy is set to raise.
        """
        pass


    