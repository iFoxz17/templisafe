class BindingError(Exception):
    """Base class for binding-related errors."""
    __slots__: tuple[str, ...] = ()
    pass

class MissingBindingError(BindingError):
    """Raised when a required binding is missing."""
    
    __slots__: tuple[str, ...] = ()

    def __init__(self, binding_name: str) -> None:
        super().__init__(binding_name, f"Missing binding with name: '{binding_name}'")