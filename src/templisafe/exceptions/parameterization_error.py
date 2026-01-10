class ParameterizationError(Exception):
    """Base class for parameterization-related exceptions."""
    
    __slots__: tuple[str, ...] = ("param_name",)

    def __init__(self, param_name: str, message: str) -> None:
        self.param_name = param_name
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(param_name={self.param_name!r}, message={self.args[0]!r})"


class MissingParameterizationError(ParameterizationError):
    """Raised when a required parameterization is missing."""
    
    __slots__: tuple[str, ...] = ()

    def __init__(self, param_name: str) -> None:
        super().__init__(param_name, f"Missing parameterization with name: '{param_name}'")