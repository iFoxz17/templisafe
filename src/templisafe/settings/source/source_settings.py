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
    HTTP = "http"
    AWS_S3_BUCKET = "aws_s3_bucket"
    AWS_SECRETS_MANAGER ="aws_secrets_manager"
    AWS_SSM_PARAMETER = "aws_ssm_parameter"
    AWS_DYNAMODB = "aws_dynamodb"
    CUSTOM = "custom"

class SourceSettings(Settings, ABC):
    """Base abstract class for defining source settings."""

    content_type: ContentType | None = None

    @property
    @abstractmethod
    def kind(self) -> SourceKind:
        """Return the kind of the source."""
        pass

    _SOURCE_KIND_MAP: ClassVar[dict[SourceKind, Type["SourceSettings"]]] = {}

    @classmethod
    def register_source_kind(cls, kind: SourceKind, klass: Type["SourceSettings"]) -> None:
        cls._SOURCE_KIND_MAP[kind] = klass

    @classmethod
    def _prepare_kwargs(cls, kwargs: dict[str, Any]) -> dict[str, Any]:
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
        """Factory method to instantiate the correct `SourceSettings` subclass."""
        prepared: dict[str, Any] = cls._prepare_kwargs(kwargs)
        target_cls: Type[SourceSettings] = prepared["target_cls"]
        kwargs = prepared["kwargs"]

        try:
            return cast("SourceSettings", target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e