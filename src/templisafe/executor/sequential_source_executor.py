from tenacity import Retrying
from templisafe.content.content import Content
from templisafe.executor.source_executor import (
    SourceExecutor, 
    SourceExecutorRequest,
    SourceExecutorResult, SourceResult
)
from templisafe.settings.source_executor_settings import SourceExecutorSettings

class SequentialSourceExecutor(SourceExecutor):
    """Executes a list of sources sequentially, one after the other."""

    def __init__(self, settings: SourceExecutorSettings, retrying: Retrying) -> None:
        super().__init__(settings=settings, retrying=retrying)
        
    def execute(self, request: SourceExecutorRequest) -> SourceExecutorResult:
        results: list[SourceResult] = [
            SourceResult(
                id=req.id, 
                content=Content(
                    payload=self._retrying(lambda : req.source.read()), 
                    type_=req.source.content_type
                )
            )
            for req in request.requests
        ]
        
        return SourceExecutorResult(results=results)        


    