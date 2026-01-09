from sqltemplater.util.util import ContentType 
from typing import Any

#---------------------------------------------------------------------------------------------
# Schema definition
#---------------------------------------------------------------------------------------------

class SchemaDefinitionError(Exception):
    """Base class for schema definition related errors."""
    pass

class IllegalSchemaDefinitionError(SchemaDefinitionError):
    """Raised when an entire schema is illegal."""
    
    __slots__: tuple[str, ...] = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal schema definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"

class UnsupportedSchemaParserError(Exception):
    """Raised when trying to instantiate a schema parser that is not implemented."""
    
    __slots__: tuple[str, ...] = ("content_type",)

    def __init__(self, content_type: ContentType) -> None:
        self.content_type = content_type
        super().__init__(f"Missing schema parser implementation for content_type: {content_type!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content_type={self.content_type!r})"

#---------------------------------------------------------------------------------------------
# Schema parsing
#---------------------------------------------------------------------------------------------

class SchemaError(Exception):
    """Base class for schema-related errors."""
    pass

class IllegalSchemaError(SchemaError):
    """Raised when an entire schema is illegal."""
    
    __slots__: tuple[str, ...] = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal schema provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"


class IllegalType(SchemaError):
    """Raised when a parameter has a type not in the allowed types."""
    
    __slots__: tuple[str, ...] = ("type_", "allowed_types", "aliases")

    def __init__(self, type_: str, allowed_types: set[str], aliases: list[str] | None = None) -> None:
        """
        Args:
            type_: The illegal type encountered (as a string).
            allowed_types: List of allowed types (as strings).
            aliases: Optional list of alternative names/aliases for types.
        """
        self.type_ = type_
        self.allowed_types = allowed_types
        self.aliases = aliases or []

        message = (
            f"Illegal type '{type_}' encountered. "
            f"Allowed types: {', '.join(allowed_types)}"
        )
        if self.aliases:
            message += f". Aliases: {', '.join(self.aliases)}"
        
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"type_={self.type_!r}, "
            f"allowed_types={self.allowed_types!r}, "
            f"aliases={self.aliases!r})"
        )

class IllegalVar(SchemaError):
    """Raised for an illegal variable in a schema."""
    
    __slots__: tuple[str, ...] = ("var_index", "var_name", "var_type")

    def __init__(self, var_index: int, var_name: str, var_type: str, msg: str) -> None:
        self.var_index = var_index
        self.var_name = var_name
        self.var_type = var_type
        super().__init__(msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(var_index={self.var_index}, "
            f"var_name={self.var_name!r}, var_type={self.var_type!r}, msg={self.args[0]!r})"
        )


class IllegalVarType(IllegalVar):
    """Raised when a variable has a type not in the allowed types."""
    
    __slots__: tuple[str, ...] = ("allowed_types",)

    def __init__(self, var_index: int, var_name: str, var_type: str, allowed_types: list[str]) -> None:
        self.allowed_types = allowed_types
        msg = (
            f"Illegal type for variable '{var_name}' at index {var_index}: {var_type}. "
            f"Allowed types: {allowed_types}"
        )
        super().__init__(var_index, var_name, var_type, msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(var_index={self.var_index}, var_name={self.var_name!r}, "
            f"var_type={self.var_type!r}, allowed_types={self.allowed_types!r})"
        )
    
class IllegalVarDefault(IllegalVar):
    """Raised when a variable has a default not of the type indicated."""
    
    __slots__: tuple[str, ...] = ("var_default",)

    def __init__(self, var_index: int, var_name: str, var_type: type, var_default: Any) -> None:
        self.var_default = var_default
        msg = (
            f"Illegal default value for variable '{var_name}' at index {var_index}: {var_default}. "
            f"Expecting type {var_type.__name__}, got {type(var_default).__name__}"
        )
        super().__init__(var_index, var_name, var_type.__name__, msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(var_index={self.var_index}, var_name={self.var_name!r}, "
            f"var_type={self.var_type!r}, default={self.var_default!r})"
        )

