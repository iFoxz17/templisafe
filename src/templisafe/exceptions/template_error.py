from templisafe.util.util import ContentType
from typing import Type

#---------------------------------------------------------------------------------------------
# QTemplateParser
#---------------------------------------------------------------------------------------------

class QTemplateParserError(Exception):
    """Base class for QTemplateParser related errors."""
    __slots__: tuple[str, ...] = ()
    pass

class QTemplateParserCreationError(Exception):
    """
    Raised when a QTemplateParser cannot be created due to
    invalid or missing loader context.
    """

    __slots__: tuple[str, ...] = ('parser_type', 'expected_context', 'actual_context', 'message')

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
        parts: list[str] = ["Failed to create qtemplate parser"]

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

class UnsupportedQTemplateParserError(QTemplateParserError):
    """Raised when trying to instantiate a QTemplateParser that is not supported."""
    
    __slots__: tuple[str, ...] = ("content_type",)

    def __init__(self, content_type: ContentType) -> None:
        self.content_type = content_type
        super().__init__(f"Missing template parser implementation for content_type: {content_type!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content_type={self.content_type!r})"

#---------------------------------------------------------------------------------------------
# QTemplate definition
#---------------------------------------------------------------------------------------------

class QTemplateDefinitionError(Exception):
    """Base class for template definition related errors."""
    __slots__: tuple[str, ...] = ()
    pass

class IllegalQTemplateDefinitionError(QTemplateDefinitionError):
    """Raised when an entire template is illegal."""
    
    __slots__: tuple[str, ...] = ("msg",)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(f"Illegal template definition provided: {msg}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(msg={self.msg!r})"
