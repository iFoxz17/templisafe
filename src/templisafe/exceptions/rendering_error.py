class RenderingError(Exception):
    """Base class for rendering-related exceptions."""
    pass

class RenderingFailureError(RenderingError):
    """Raised when template rendering fails."""

    __slots__: tuple[str, ...] = ("rendering",)

    def __init__(self, rendering) -> None:
        self.rendering = rendering

        # Base message
        message_lines = [
            f"Template rendering failed with outcome {rendering.outcome.name}: {rendering.message}"
        ]

        # Append diagnostics if any
        if rendering.diagnostics:
            message_lines.append("Diagnostics:")
            for diag in rendering.diagnostics:
                message_lines.append(f"[{diag.level.name}] binding={diag.name}: {diag.message}")

        # Join all lines into the final message
        full_message: str = "\n".join(message_lines)

        super().__init__(full_message)
