from typing import Any

class HttpSessionError(Exception):
    """Base class for HTTP session-related exceptions."""
    __slots__: tuple[str, ...] = ()

class HttpSessionOverflowError(HttpSessionError):
    """Raised when attempting to create more HTTP sessions than the allowed maximum."""
    __slots__: tuple[str, ...] = ("max_sessions",)

    def __init__(self, max_sessions: int | None = None) -> None:
        self.max_sessions = max_sessions
        
        message = f"HTTP sessions overflow: cannot exceed max number of sessions"
        if max_sessions:
            message += f" ({max_sessions})"
        
        super().__init__(message)
