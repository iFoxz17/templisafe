from typing import Iterable
from templisafe.executor.source_executor import SourceRequest
from templisafe.settings.source_executor_settings import SourceExecutorStrategy
from templisafe.source.source import Source
from templisafe.settings.source_strategy_optimizer_settings import StrategyOptimizerSettings, SourceLatencyProfile

class StrategyOptimizer:
    """Optimizes the execution strategy for a list of sources based on their latency profile."""

    __slots__: tuple[str, ...] = ("_settings", "_weight_map")

    def __init__(self, settings: StrategyOptimizerSettings) -> None: 
        self._settings: StrategyOptimizerSettings = settings
        self._weight_map: dict[type, int] = self._build_weight_map()

    def _build_weight_map(self) -> dict[type, int]:
        """Precompute source type -> weight mapping for fast lookup."""
        
        settings: StrategyOptimizerSettings = self._settings
        wmap: dict[type, int] = {}
        for source_type, profile in self._settings.source_latency_map.items():
            weight: int = 0
            match profile:
                case SourceLatencyProfile.NONE:
                    weight = settings.no_latency_weight
                case SourceLatencyProfile.LOW:
                    weight = settings.low_latency_weight
                case SourceLatencyProfile.HIGH:
                    weight = settings.high_latency_weight
            wmap[source_type] = weight
        return wmap

    def _source_weight(self, source: Source) -> int:
        return self._weight_map.get(type(source), self._settings.default_latency_weight)

    def strategy(self, sources: Iterable[Source]) -> SourceExecutorStrategy:
        """
        Determine the (sub)optimal execution strategy for a list of sources.

        Parameters
        ----------
        request : Iterable[Source]
            The sources to evaluate for execution.

        Returns
        -------
        SourceExecutorStrategy
            The determined (sub)optimal strategy.
        """
        
        total_weight: int = 0
        for s in sources:
            total_weight += self._source_weight(s)
            if total_weight >= self._settings.threshold:
                return SourceExecutorStrategy.THREAD_POOL
        
        return SourceExecutorStrategy.SEQUENTIAL