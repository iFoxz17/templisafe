from abc import ABC, abstractmethod
from typing import Type, Any, ClassVar, cast
from pydantic import ValidationError
from enum import Enum
from overrides import overrides

from templisafe.settings.settings import Settings
from templisafe.util.util import ContentType


class SourceKind(str, Enum):
    INLINE = "inline"
    LOCAL = "local"


class SourceSettings(Settings, ABC):
    """Base class for all source settings."""

    content_type: ContentType | None = None

    # -----------------------------
    # Polymorphic kind
    # -----------------------------
    @property
    @abstractmethod
    def kind(self) -> SourceKind:
        """Return the kind of the source."""
        pass

    # -----------------------------
    # Factory for polymorphic creation
    # -----------------------------
    _SOURCE_KIND_MAP: ClassVar[dict[SourceKind, Type["SourceSettings"]]] = {}

    @classmethod
    def register_source_kind(cls, kind: SourceKind, klass: Type["SourceSettings"]) -> None:
        cls._SOURCE_KIND_MAP[kind] = klass

    @classmethod
    def _prepare_kwargs(cls, kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize 'kind', validate presence and select target subclass.
        Returns {'target_cls': <subclass>, 'kwargs': normalized kwargs}.
        """
        kind: Any = kwargs.pop("kind", None)
        if kind is None:
            raise ValueError("Missing 'kind' field to determine source type")

        if isinstance(kind, str):
            try:
                kind = SourceKind(kind.lower())
            except ValueError:
                raise ValueError(f"Invalid kind: {kind!r}")

        target_cls: Type[SourceSettings] | None = cls._SOURCE_KIND_MAP.get(kind)
        if target_cls is None:
            raise ValueError(f"No SourceSettings class registered for kind {kind!r}")

        return {"target_cls": target_cls, "kwargs": kwargs}

    @classmethod
    @overrides
    def _parse_config(cls, config: dict[str, Any]) -> "SourceSettings":
        """
        Convert a dict from YAML/JSON/dict into the correct SourceSettings subclass.
        """
        prepared: dict[str, Any] = cls._prepare_kwargs(config)
        target_cls: Type[SourceSettings] = prepared["target_cls"]
        kwargs: dict[str, Any] = prepared["kwargs"]

        try:
            return cast("SourceSettings", target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e

    @classmethod
    @overrides
    def create(cls, **kwargs) -> "SourceSettings":
        """
        Public factory to instantiate the correct SourceSettings subclass.
        """
        prepared: dict[str, Any] = cls._prepare_kwargs(kwargs)
        target_cls: Type[SourceSettings] = prepared["target_cls"]
        kwargs = prepared["kwargs"]

        try:
            return cast("SourceSettings", target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e


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


# Register subclasses
SourceSettings.register_source_kind(SourceKind.INLINE, InlineSourceSettings)
SourceSettings.register_source_kind(SourceKind.LOCAL, LocalSourceSettings)
