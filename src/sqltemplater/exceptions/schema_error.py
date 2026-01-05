from sqltemplater.util.util import ContentType 

#---------------------------------------------------------------------------------------------
# Schema definition
#---------------------------------------------------------------------------------------------

class SchemaDefinitionError(Exception):
    """Base class for schema definition related errors."""
    pass

class IllegalSchemaDefinitionError(SchemaDefinitionError):
    """Raised when an entire schema is illegal."""
    
    __slots__ = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal schema definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"

class UnimplementedSchemaParserError(Exception):
    """Raised when trying to instantiate a schema parser that is not implemented."""
    
    __slots__ = ("content_type",)

    def __init__(self, content_type: ContentType) -> None:
        self.content_type = content_type
        super().__init__(f"Missing schema parser implementation for content_type: {content_type!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content_type={self.content_type!r})"

#---------------------------------------------------------------------------------------------
# Schema
#---------------------------------------------------------------------------------------------

class SchemaError(Exception):
    """Base class for schema-related errors."""
    pass

class IllegalSchemaError(SchemaError):
    """Raised when an entire schema is illegal."""
    
    __slots__ = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal schema provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"


class IllegalType(SchemaError):
    """Raised when a parameter has a type not in the allowed types."""
    
    __slots__ = ("type_", "allowed_types", "aliases")

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

class IllegalParam(SchemaError):
    """Raised for an illegal parameter in a schema."""
    
    __slots__ = ("p_index", "p_name", "p_type")

    def __init__(self, p_index: int, p_name: str, p_type: str, msg: str) -> None:
        self.p_index = p_index
        self.p_name = p_name
        self.p_type = p_type
        super().__init__(msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(p_index={self.p_index}, "
            f"p_name={self.p_name!r}, p_type={self.p_type!r}, msg={self.args[0]!r})"
        )


class IllegalParamType(IllegalParam):
    """Raised when a parameter has a type not in the allowed types."""
    
    __slots__ = ("allowed_types",)

    def __init__(self, p_index: int, p_name: str, p_type: str, allowed_types: list[str]) -> None:
        self.allowed_types = allowed_types
        msg = (
            f"Illegal type for parameter {p_index} ('{p_name}'): {p_type}. "
            f"Allowed types: {allowed_types}"
        )
        super().__init__(p_index, p_name, p_type, msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(p_index={self.p_index}, p_name={self.p_name!r}, "
            f"p_type={self.p_type!r}, allowed_types={self.allowed_types!r})"
        )
    
    
class DuplicatedParamError(SchemaError):
    """Error when a parameter is duplicated in the schema."""
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


