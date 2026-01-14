class VariantError(Exception):
    """Base class for variant-related exceptions."""

class IllegalVariantError(VariantError):
    """Raised when a variant definition is illegal."""
    
    __slots__: tuple[str, ...] = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal variant provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"