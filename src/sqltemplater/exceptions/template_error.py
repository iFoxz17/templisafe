from sqltemplater.util.util import ContentType
from typing import Type

#---------------------------------------------------------------------------------------------
# Template parser
#---------------------------------------------------------------------------------------------

class TemplateParserError(Exception):
    """Base class for template parser related errors."""
    pass

class TemplateParserCreationError(Exception):
    """
    Raised when a TemplateParser cannot be created due to
    invalid or missing loader context.
    """

    def __init__(
        self,
        parser_type: ContentType | None = None,
        expected_context: Type | None = None,
        actual_context: object | None = None,
    ) -> None:
        self.parser_type = parser_type
        self.expected_context = expected_context
        self.actual_context = actual_context

        message = self._build_message()
        super().__init__(message)

    def _build_message(self) -> str:
        parts: list[str] = ["Failed to create template parser"]

        if self.parser_type is not None:
            parts.append(f"for parser type '{self.parser_type.name}'")

        if self.expected_context is not None:
            parts.append(
                f"(expected context: {self.expected_context.__name__})"
            )

        if self.actual_context is not None:
            parts.append(
                f"(received: {type(self.actual_context).__name__})"
            )

        return " ".join(parts)

class UnimplementedTemplateParserError(TemplateParserError):
    """Raised when trying to instantiate a template parser that is not implemented."""
    
    __slots__ = ("content_type",)

    def __init__(self, content_type: ContentType) -> None:
        self.content_type = content_type
        super().__init__(f"Missing template parser implementation for content_type: {content_type!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content_type={self.content_type!r})"

#---------------------------------------------------------------------------------------------
# Template definition
#---------------------------------------------------------------------------------------------

class TemplateDefinitionError(Exception):
    """Base class for template definition related errors."""
    pass

class IllegalTemplateDefinitionError(TemplateDefinitionError):
    """Raised when an entire template is illegal."""
    
    __slots__ = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal template definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"
