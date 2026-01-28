from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import List

from tenacity import Retrying

from templisafe.content.content import Content
from templisafe.executor.source_executor import (
    SourceExecutor,
    SourceExecutorRequest, SourceRequest,
    SourceExecutorResult, SourceResult
)
from templisafe.settings.source_executor_settings import SourceExecutorSettings

class ThreadPoolSourceExecutor(SourceExecutor):
    """Execute sources concurrently using a `ThreadPoolExecutor`."""

    __slots__: tuple[str, ...] = ("_settings", "_max_workers", "_retrying")

    def __init__(self, settings: SourceExecutorSettings, retrying: Retrying) -> None:
        super().__init__(settings=settings, retrying=retrying)
        self._max_workers: int | None = settings.n_threads
        self._settings: SourceExecutorSettings = settings

    def execute(self, request: SourceExecutorRequest) -> SourceExecutorResult:
        results: List[SourceResult] = [None] * len(request.requests)  # type: ignore

        def worker(idx: int, req: SourceRequest) -> tuple[int, SourceResult]:
            content: Content = Content(
                payload=self._retrying(lambda: req.source.read()), 
                type_=req.source.content_type
            )
            return idx, SourceResult(id=req.id, content=content)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(worker, idx, req) 
                for idx, req 
                in enumerate(request.requests)
            ]
            for future in as_completed(futures):
                idx, content = future.result() 
                results[idx] = content

        return SourceExecutorResult(results=results)
