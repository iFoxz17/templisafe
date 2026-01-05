from typing import Any

class ParamError(Exception):
    """Base class for parameter-related exceptions."""
    
    __slots__ = ("param",)

    def __init__(self, param: str, message: str) -> None:
        self.param = param
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(param={self.param!r}, message={self.args[0]!r})"


class MissingParamError(ParamError):
    """Raised when a required parameter is missing."""
    
    __slots__ = ()

    def __init__(self, param: str) -> None:
        super().__init__(param, f"Missing parameter: '{param}'")


class ParamTypeError(ParamError):
    """Raised when a parameter has the wrong type."""
    
    __slots__ = ("expected", "actual")

    def __init__(self, param: str, expected: type[Any], actual: type) -> None:
        self.expected = expected
        self.actual = actual
        message = (
            f"Wrong type for parameter '{param}': "
            f"expecting '{expected.__name__}', got '{actual.__name__}'"
        )
        super().__init__(param, message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(param={self.param!r}, "
            f"expected={self.expected.__name__!r}, actual={self.actual.__name__!r})"
        )
