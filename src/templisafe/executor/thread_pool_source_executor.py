from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from tenacity import RetryError

from templisafe.content.content import Content
from templisafe.executor.source_executor import (
    SourceExecutor,
    SourceExecutorRequest, SourceRequest,
    SourceExecutorResult, SourceResult
)
from templisafe.settings.source_executor_settings import SourceExecutorSettings

class ThreadPoolSourceExecutor(SourceExecutor):
    """Execute sources concurrently using a `ThreadPoolExecutor`."""

    __slots__ = ("_settings", "_max_workers", "_retrying")

    def __init__(self, settings: SourceExecutorSettings) -> None:
        super().__init__(settings=settings)
        self._max_workers = settings.n_threads
        self._settings: SourceExecutorSettings = settings

    def execute(self, request: SourceExecutorRequest) -> SourceExecutorResult:
        results: List[SourceResult] = [None] * len(request.requests)  # type: ignore

        def worker(idx: int, req: SourceRequest) -> None:
            """Read a source with retry and store in the correct index."""
            try:
                content = self._retrying(
                    lambda: Content(payload=req.source.read(), type_=req.source.content_type)
                )
            except RetryError as e:
                # If reraise=True, this will already raise; else fallback
                content = e.last_attempt.result()
            results[idx] = SourceResult(id=req.id, content=content)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [
                executor.submit(worker, idx, req) 
                for idx, req 
                in enumerate(request.requests)
            ]
            for future in as_completed(futures):
                future.result()  # propagate exceptions

        return SourceExecutorResult(results=results)
