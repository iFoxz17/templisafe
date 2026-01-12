from abc import ABC
from overrides import overrides
from typing import Type, TypeVar, Dict, Any, ClassVar, cast

from templisafe.util.util import ContentType
from templisafe.settings.parser.parser_settings import ParserSettings

T = TypeVar("T", bound="VariantParserSettings")


class VariantParserSettings(ParserSettings, ABC):
    """Settings for parsers that handle variants."""
    variants_key: str
    default_variants_name: str

    # -----------------------------
    # Subclass registry for dispatch
    # -----------------------------
    _CONTENT_TYPE_MAP: ClassVar[Dict[ContentType, Type["VariantParserSettings"]]] = {}

    @classmethod
    def register_content_type(cls, content_type: ContentType, klass: Type["VariantParserSettings"]) -> None:
        cls._CONTENT_TYPE_MAP[content_type] = klass

    # -----------------------------
    # Factory / creation methods
    # -----------------------------
    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """
        Create a VariantParserSettings instance.

        Dispatches to a concrete subclass based on 'content_type' if provided.
        """
        kind: Any = kwargs.pop("kind", None)

        # Dispatch to concrete subclass
        target_cls: Type["VariantParserSettings"]
        if kind is not None:
            if isinstance(kind, str):
                try:
                    kind = ContentType(kind.lower())
                except ValueError:
                    raise ValueError(f"Invalid kind: {kind!r}")
            maybe_target_cls: Type["VariantParserSettings"] | None = cls._CONTENT_TYPE_MAP.get(kind)
            if maybe_target_cls is None:
                raise ValueError(f"No VariantParserSettings registered for kind {kind!r}")
            target_cls = maybe_target_cls
        else:
            if cls is VariantParserSettings:
                raise ValueError(f"Missing kind field for concrete class dispacth")
            target_cls = cls

        # Validate required fields
        variants_key: Any = kwargs.get("variants_key")
        if variants_key is None:
            raise ValueError("Missing 'variants_key' field")

        default_variants_name: Any = kwargs.get("default_variants_name")
        if default_variants_name is None:
            raise ValueError("Missing 'default_variants_name' field")

        # Pydantic validation
        try:
            return cast(T, target_cls.model_validate({
                "variants_key": variants_key,
                "default_variants_name": default_variants_name
            }))
        except Exception as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e

    @classmethod
    def _parse_config(cls: Type[T], config: Dict[str, Any]) -> T:
        """Used by Settings.from_yaml/from_json/from_dict."""
        if not isinstance(config, dict):
            raise ValueError(f"Expected a dict, got {type(config).__name__}")
        return cls.create(**config)


class YamlVariantParserSettings(VariantParserSettings):
    @property
    @overrides
    def kind(self) -> ContentType:
        return ContentType.YAML


# Register the concrete YAML parser
VariantParserSettings.register_content_type(ContentType.YAML, YamlVariantParserSettings)
