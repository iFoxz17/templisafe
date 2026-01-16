class CompilationError(Exception):
    """Base class for compilation-related exceptions."""
    pass

class CompilationFailureError(CompilationError):
    """Raised when a template compilation fails."""

    __slots__: tuple[str, ...] = ("compilation",)

    def __init__(self, compilation) -> None:
        self.compilation = compilation

        # Base message
        message_lines = [
            f"Template compilation failed with outcome {compilation.outcome.name}: "
            f"{compilation.message}"
        ]

        # Append diagnostics if any
        if compilation.diagnostics:
            message_lines.append("Diagnostics:")
            for diag in compilation.diagnostics:
                message_lines.append(
                    f"[{diag.level.name}] variable={diag.name}: {diag.message}"
                )

        # Join all lines into the final message
        full_message: str = "\n".join(message_lines)

        super().__init__(full_message)