from pathlib import Path
from typing import Any


class SourceError(Exception):
    """Base class for source-related exceptions."""

    pass


class MissingContentTypeError(SourceError):
    """Raised when trying to create a source without a content type."""

    __slots__: tuple[str, ...] = ("settings",)

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        message = f"Cannot create a source without its content type: {settings}"
        super().__init__(message)


class UninitializedSourceError(Exception):
    """Raised when a source is used before calling `open`."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("Source was not opened: call `open()` before reading.")


class LocalSourceError(SourceError):
    """Raised when a local source file cannot be found."""

    __slots__: tuple[str, ...] = ("path",)

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"File not found: {path!r}")


class HttpSourceError(SourceError):
    """Raised when an HTTP source cannot be fetched."""

    __slots__ = ("url", "status_code")

    def __init__(self, url: str, status_code: int | None = None) -> None:
        self.url = url
        self.status_code = status_code
        msg = f"Failed to fetch URL {url!r}"
        if status_code:
            msg += f": GET method returned status code {status_code}"
        super().__init__(msg)


class AwsSourceError(Exception):
    """Raised when an aws source cannot be accessed or read."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class UnsupportedSourceError(SourceError):
    """Raised when trying to instantiate a source that is not supported."""

    __slots__: tuple[str, ...] = ("settings",)

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        super().__init__(f"Missing source implementation for settings: {settings!r}")


class ContentTypeResolutionError(SourceError):
    """Raised when the content type of a source cannot be resolved."""

    __slots__: tuple[str, ...] = ("settings",)

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        message = f"Unable to resolve content type for settings {settings}"
        super().__init__(message)
