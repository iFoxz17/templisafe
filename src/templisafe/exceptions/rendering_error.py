from abc import ABC
# from templisafe.query.query_model import QRendering

class RenderingError(Exception, ABC):
    """Raised when query rendering fails or violates diagnostic policy."""
    pass

class RenderingFailureError(RenderingError):

    __slots__: tuple[str, ...] = ("rendering",)

    def __init__(self, rendering) -> None:
        self.rendering = rendering

        # Base message
        message_lines = [
            f"Query rendering failed with outcome {rendering.outcome.name}: {rendering.message}"
        ]

        # Append diagnostics if any
        if rendering.diagnostics:
            message_lines.append("Diagnostics:")
            for diag in rendering.diagnostics:
                message_lines.append(f"[{diag.level.name}] binding={diag.name}: {diag.message}")

        # Join all lines into the final message
        full_message: str = "\n".join(message_lines)

        super().__init__(full_message)
