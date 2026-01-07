from sqltemplater.util.util import ContentType 
from typing import Any

#---------------------------------------------------------------------------------------------
# Parameters definition
#---------------------------------------------------------------------------------------------

class ParamsDefinitionError(Exception):
    """Base class for params definition related errors."""
    __slots__: tuple[str, ...] = ()
    pass

class IllegalParamsDefinitionError(ParamsDefinitionError):
    """Raised when an entire params is illegal."""
    
    __slots__: tuple[str, ...] = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal parameters definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"

class UnsupportedQVariantParserError(Exception):
    """Raised when trying to instantiate a QVariantParser that is not implemented."""
    
    __slots__: tuple[str, ...] = ("content_type",)

    def __init__(self, content_type: ContentType) -> None:
        self.content_type = content_type
        super().__init__(f"Missing QVariantParser implementation for content_type: {content_type!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content_type={self.content_type!r})"

#---------------------------------------------------------------------------------------------
# Bindings
#---------------------------------------------------------------------------------------------

class BindingError(Exception):
    """Base class for binding-related errors."""
    __slots__: tuple[str, ...] = ()
    pass

class MissingBindingError(BindingError):
    """Raised when a required binding is missing."""
    
    __slots__: tuple[str, ...] = ()

    def __init__(self, binding_name: str) -> None:
        super().__init__(binding_name, f"Missing binding with name: '{binding_name}'")

class IllegalVariantError(BindingError):
    """Raised when an entire params is illegal."""
    
    __slots__: tuple[str, ...] = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal parameters provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"

class IllegalParam(BindingError):
    """Raised for an illegal parameter in a params."""
    
    __slots__: tuple[str, ...] = ("p_index", "p_name", "p_value")

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


class DuplicatedBindingError(BindingError):
    """Error when a binding is duplicated in the definition."""
    __slots__: tuple[str, ...] = ("b_name", "first_index", "second_index")

    def __init__(self, b_name: str, first_index: int, second_index: int) -> None:
        self.b_name = b_name
        self.first_index = first_index
        self.second_index = second_index
        message = (
            f"Binding '{b_name}' is duplicated: "
            f"first occurrence at index {first_index}, "
            f"second occurrence at index {second_index}"
        )
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(b_name={self.b_name!r}, "
            f"first_index={self.first_index}, second_index={self.second_index})"
        )


