from sqltemplater.util.util import ContentType 
from typing import Any

#---------------------------------------------------------------------------------------------
# Parameters definition
#---------------------------------------------------------------------------------------------

class ParamsDefinitionError(Exception):
    """Base class for params definition related errors."""
    pass

class IllegalParamsDefinitionError(ParamsDefinitionError):
    """Raised when an entire params is illegal."""
    
    __slots__ = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal parameters definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"

class UnimplementedParamsParserError(Exception):
    """Raised when trying to instantiate a params parser that is not implemented."""
    
    __slots__ = ("content_type",)

    def __init__(self, content_type: ContentType) -> None:
        self.content_type = content_type
        super().__init__(f"Missing params parser implementation for content_type: {content_type!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content_type={self.content_type!r})"

#---------------------------------------------------------------------------------------------
# Params
#---------------------------------------------------------------------------------------------

class ParamsError(Exception):
    """Base class for params-related errors."""
    pass

class IllegalParamsError(ParamsError):
    """Raised when an entire params is illegal."""
    
    __slots__ = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal parameters provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"

class IllegalParam(ParamsError):
    """Raised for an illegal parameter in a params."""
    
    __slots__ = ("p_index", "p_name", "p_value")

    def __init__(self, p_index: int, p_name: str, p_value: Any, msg: str) -> None:
        self.p_index = p_index
        self.p_name = p_name
        self.p_value = p_value
        super().__init__(msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(p_index={self.p_index}, "
            f"p_name={self.p_name!r}, p_value={self.p_value!r}, msg={self.args[0]!r})"
        )


class DuplicatedParamError(ParamsError):
    """Error when a parameter is duplicated in the params."""
    __slots__ = ("p_name", "first_index", "second_index")

    def __init__(self, p_name: str, first_index: int, second_index: int) -> None:
        """
        Args:
            p_name: Name of the duplicated parameter.
            first_index: Index or position of the first occurrence.
            second_index: Index or position of the second occurrence.
        """
        self.p_name = p_name
        self.first_index = first_index
        self.second_index = second_index
        message = (
            f"Parameter '{p_name}' is duplicated: "
            f"first occurrence at index {first_index}, "
            f"second occurrence at index {second_index}"
        )
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(p_name={self.p_name!r}, "
            f"first_index={self.first_index}, second_index={self.second_index})"
        )


