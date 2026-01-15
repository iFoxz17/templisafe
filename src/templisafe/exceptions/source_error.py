from pathlib import Path
from templisafe.source.source import SourceSettings

class SourceError(Exception):
    """Base class for source-related exceptions."""
    pass


class LocalSourceError(SourceError):
    """Raised when a local source file cannot be found."""
    
    __slots__: tuple[str, ...] = ("path",)

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"File not found: {path!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r})"

class UnsupportedSourceError(SourceError):
    """Raised when trying to instantiate a source that is not supported."""
    
    __slots__: tuple[str, ...] = ("settings",)

    def __init__(self, settings: SourceSettings) -> None:
        self.settings = settings
        super().__init__(f"Missing source implementation for settings: {settings!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(settings={self.settings!r})"
    
class ContentTypeResolutionError(SourceError):
    """Raised when the content type of a source cannot be resolved."""

    __slots__: tuple[str, ...] = ("settings",)

    def __init__(self, settings: SourceSettings) -> None:
        self.settings = settings
        message = f"Unable to resolve content type for settings {settings}"
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(settings={self.settings!r})"



