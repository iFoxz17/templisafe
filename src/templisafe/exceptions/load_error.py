class LoadError(Exception):
    """Base class for loader-related exceptions."""
    pass

class UnsopportedLoadError(LoadError):
    """Raised when trying to load an unsupported content type."""
    pass