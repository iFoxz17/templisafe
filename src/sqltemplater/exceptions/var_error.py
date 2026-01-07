from typing import Any

class VarError(Exception):
    """Base class for variables-related exceptions."""
    
    __slots__ = ("var_name",)

    def __init__(self, var_name: str, message: str) -> None:
        self.var_name = var_name
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(var_name={self.var_name!r}, message={self.args[0]!r})"


class MissingVarError(VarError):
    """Raised when a required variable is missing."""
    
    __slots__ = ()

    def __init__(self, var_name: str) -> None:
        super().__init__(var_name, f"Missing variable with name: '{var_name}'")


class VarTypeError(VarError):
    """Raised when a variable has the wrong type."""
    
    __slots__ = ("expected", "actual")

    def __init__(self, var: str, expected: type[Any], actual: type) -> None:
        self.expected = expected
        self.actual = actual
        message = (
            f"Wrong type for variable '{var}': "
            f"expecting '{expected.__name__}', got '{actual.__name__}'"
        )
        super().__init__(var, message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(var_name={self.var_name!r}, "
            f"expected={self.expected.__name__!r}, actual={self.actual.__name__!r})"
        )
