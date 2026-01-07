from pathlib import Path
from sqltemplater.source.source import SourceSettings

class SourceError(Exception):
    """Base class for source-related exceptions."""
    pass


class LocalSourceError(SourceError):
    """Raised when a local source file cannot be found."""
    
    __slots__ = ("path",)

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"File not found: {path!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r})"


class UnsupportedSourceError(SourceError):
    """Raised when trying to instantiate a source that is not supported."""
    
    __slots__ = ("settings",)

    def __init__(self, settings: SourceSettings) -> None:
        self.settings = settings
        super().__init__(f"Missing source implementation for settings: {settings!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(settings={self.settings!r})"
