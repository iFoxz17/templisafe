from abc import ABC, abstractmethod
from overrides import overrides
from typing import Type, Any, ClassVar
from pydantic import BaseModel, ConfigDict, ValidationError
from enum import Enum

from sqltemplater.util.util import ContentType

class SourceKind(str, Enum):
    INLINE = "inline"
    LOCAL = "local"

class SourceSettings(BaseModel, ABC):
    """Base class for all source settings."""
    content_type: ContentType | None = None

    @property
    @abstractmethod
    def kind(self) -> SourceKind:
        pass

    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )

    # -----------------------------
    # Factory for polymorphic creation
    # -----------------------------
    _KIND_MAP: ClassVar[dict[SourceKind, Type["SourceSettings"]]] = {}

    @classmethod
    def register_kind(cls, kind: SourceKind, klass: Type["SourceSettings"]) -> None:
        cls._KIND_MAP[kind] = klass

    @classmethod
    def create(cls, **kwargs) -> "SourceSettings":
        """ Create the appropriate SourceSettings subclass based on 'kind'."""
        kind: Any = kwargs.pop("kind")
        if kind is None:
            raise ValueError("Missing 'kind' field to determine source type")
        if isinstance(kind, str):
            try:
                kind = SourceKind(kind)
            except ValueError:
                raise ValueError(f"Invalid kind: {kind!r}")

        klass: Type["SourceSettings"] | None = cls._KIND_MAP.get(kind)
        if klass is None:
            raise ValueError(f"No SourceSettings class registered for kind {kind!r}")
        try:
            return klass.model_validate(kwargs) 
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {klass.__name__}: {e}") from e


# ---------------------------------------------------------------------------
# Concrete source settings
# ---------------------------------------------------------------------------
class InlineSourceSettings(SourceSettings):
    content: str

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.INLINE

class LocalSourceSettings(SourceSettings):
    path: str

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.LOCAL

# Register kinds with the base class
SourceSettings.register_kind(SourceKind.INLINE, InlineSourceSettings)
SourceSettings.register_kind(SourceKind.LOCAL, LocalSourceSettings)
