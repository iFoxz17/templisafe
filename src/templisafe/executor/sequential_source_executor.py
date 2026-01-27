from templisafe.content.content import Content
from templisafe.executor.source_executor import (
    SourceExecutor, 
    SourceExecutorRequest,
    SourceExecutorResult, SourceResult
)
from templisafe.settings.source_executor_settings import SourceExecutorSettings

class SequentialSourceExecutor(SourceExecutor):
    """Executes a list of sources sequentially, one after the other."""

    def __init__(self, settings: SourceExecutorSettings) -> None:
        super().__init__(settings=settings)
        
    def execute(self, request: SourceExecutorRequest) -> SourceExecutorResult:
        return SourceExecutorResult(
            results=[
                self._retrying(
                    lambda : SourceResult(
                        id=req.id, 
                        content=Content(
                            payload=req.source.read(), 
                            type_=req.source.content_type
                        )
                    )
                )
                for req in request.requests
            ]
        )        


    