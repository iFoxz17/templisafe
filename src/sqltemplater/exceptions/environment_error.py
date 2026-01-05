#---------------------------------------------------------------------------------------------
# Environment definition
#---------------------------------------------------------------------------------------------

class EnvironmentDefinitionError(Exception):
    """Base class for environment definition related errors."""
    pass

class IllegalEnvironmentDefinitionError(EnvironmentDefinitionError):
    """Raised when an entire environment is illegal."""
    
    __slots__ = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal environment definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"
