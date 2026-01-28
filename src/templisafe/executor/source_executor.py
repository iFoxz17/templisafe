from abc import ABC, abstractmethod
from dataclasses import dataclass
from tenacity import Retrying

from templisafe.content.content import Content
from templisafe.source.source import Source
from templisafe.settings.source_executor_settings import SourceExecutorSettings

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

    def __init__(self, settings: SourceExecutorSettings, retrying: Retrying) -> None:
        self._settings: SourceExecutorSettings = settings
        self._retrying: Retrying = retrying
    
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
            Exceptions raised during the sources execution.
        """
        pass


    