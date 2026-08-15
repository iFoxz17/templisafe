from dataclasses import dataclass

from templisafe.content.content import Content
from templisafe.executor.source_executor import (
    SourceExecutor,
    SourceExecutorRequest,
    SourceExecutorResult,
    SourceRequest,
)
from templisafe.executor.source_executor_resolver import SourceExecutorResolver
from templisafe.executor.strategy_optimizer import StrategyOptimizer
from templisafe.settings.source_executor_settings import (
    SourceExecutorSettings,
    SourceExecutorStrategy,
)
from templisafe.source.source import Source

# ---------------------------------------------------------------------------------------------
# Source group
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SourceGroup:
    """
    Represents a collection of sources identified by a unique string key.

    Attributes
    ----------
    sources : dict[str, Source]
        A mapping of source IDs to their respective `Source` instances.
    """

    sources: dict[str, Source]


# ---------------------------------------------------------------------------------------------
# Data group
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ContentGroup:
    """
    Represents a collection of resolved content from sources.

    Attributes
    ----------
    contents : dict[str, Content]
        A mapping of source IDs to their corresponding `Content`.
    """

    contents: dict[str, Content]


# ---------------------------------------------------------------------------------------------
# Data provider
# ---------------------------------------------------------------------------------------------


class ContentProvider:
    """Provides the content of a group of sources."""

    __slots__: tuple[str, ...] = ("_source_executor_resolver", "_strategy_optimizer")

    def __init__(
        self,
        source_executor_resolver: SourceExecutorResolver,
        strategy_optimizer: StrategyOptimizer,
    ) -> None:
        self._source_executor_resolver: SourceExecutorResolver = source_executor_resolver
        self._strategy_optimizer: StrategyOptimizer = strategy_optimizer

    def _create_request(self, source_group: SourceGroup) -> SourceExecutorRequest:
        return SourceExecutorRequest([SourceRequest(id=id, source=s) for id, s in source_group.sources.items()])

    def _create_content_group(self, result: SourceExecutorResult) -> ContentGroup:
        return ContentGroup({r.id: r.content for r in result.results})

    def provide(
        self,
        source_group: SourceGroup,
        source_executor: SourceExecutor | SourceExecutorSettings | None = None,
    ) -> ContentGroup:
        """
        Provide a `ContentGroup` by executing the sources in the given `SourceGroup`.

        Parameters
        ----------
        source_group : SourceGroup
            A group of sources to be executed.
        source_executor : SourceExecutor | SourceExecutorSettings | None
            Optionally, a specific executor or settings. If `None`, or if settings do not specify a strategy,
            one will be selected using the `StrategyOptimizer`.

        Returns
        -------
        ContentGroup
            The resolved content for all sources.
        """

        optimize: bool = False
        if source_executor is None:
            source_executor = self._source_executor_resolver.default_settings
            # Default settings could already have a strategy, but we want to optimize int his case
            optimize = True

        if isinstance(source_executor, SourceExecutorSettings):
            if optimize or not source_executor.has_strategy:
                strategy: SourceExecutorStrategy = self._strategy_optimizer.strategy(source_group.sources.values())
                source_executor = source_executor.model_copy(update={"strategy": strategy})

        executor: SourceExecutor = self._source_executor_resolver.resolve(source_executor)

        request: SourceExecutorRequest = self._create_request(source_group)
        result: SourceExecutorResult = executor.execute(request)
        data_group: ContentGroup = self._create_content_group(result)
        return data_group
