from sqltemplater.query.query_renderer import RenderingResult

class RenderingError(Exception):
    """Raised when query rendering fails or violates diagnostic policy."""

    def __init__(self, rendering_result: RenderingResult):
        self.rendering_result: RenderingResult = rendering_result
        # Collect messages including diagnostics
        diag_msgs = [
            f"[{d.level.name}] param={d.param}: {d.message}"
            for d in rendering_result.diagnostics
        ]
        message = (
            f"Query rendering failed with outcome {rendering_result.outcome.name}: "
            f"{rendering_result.message}\nDiagnostics:\n" + "\n".join(diag_msgs)
            if diag_msgs else f"Query rendering failed with outcome {rendering_result.outcome.name}: "
            f"{rendering_result.message}"
        )
        super().__init__(message)
