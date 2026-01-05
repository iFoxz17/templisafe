from sqltemplater.query.query_compiler import CompilationResult

class CompilationError(Exception):
    """Raised when query compilation fails or violates diagnostic policy."""

    def __init__(self, compilation_result: CompilationResult):
        self.compilation_result: CompilationResult = compilation_result
        # Collect messages including diagnostics
        diag_msgs = [
            f"[{d.level.name}] param={d.param} index={d.index}: {d.message}"
            for d in compilation_result.diagnostics
        ]
        message = (
            f"Query compilation failed with outcome {compilation_result.outcome.name}: "
            f"{compilation_result.message}\nDiagnostics:\n" + "\n".join(diag_msgs)
            if diag_msgs else f"Query compilation failed with outcome {compilation_result.outcome.name}: "
            f"{compilation_result.message}"
        )
        super().__init__(message)