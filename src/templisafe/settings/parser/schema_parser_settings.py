from abc import ABC
from overrides import overrides
from typing import Dict, List, Tuple, Any, Type, TypeVar, cast, ClassVar
from pydantic import Field, model_validator, ValidationError

from templisafe.settings.parser.parser_settings import ParserSettings
from templisafe.util.util import ContentType

T = TypeVar("T", bound="SchemaParserSettings")


class SchemaParserSettings(ParserSettings, ABC):
    schema_key: str
    type_key: str
    default_key: str
    constraints_key: str
    metadata_key: str
    index_key: str
    model_name: str
    allowed_types: Tuple[str, ...] = Field(default_factory=tuple)
    type_aliases: frozenset[tuple[str, tuple[str, ...]]] = Field(default_factory=frozenset)

    # Registry for dispatch based on ContentType
    _KIND_MAP: ClassVar[dict[ContentType, Type["SchemaParserSettings"]]] = {}

    @classmethod
    def register_kind(cls, kind: ContentType, klass: Type["SchemaParserSettings"]) -> None:
        cls._KIND_MAP[kind] = klass

    @model_validator(mode="before")
    def convert_type_aliases(cls, values: Dict[str, Any]):
        """Convert user-provided dict to frozenset automatically."""
        aliases: Any = values.get("type_aliases", {})
        if not isinstance(aliases, dict):
            raise TypeError(f"aliases must be a dict, got {aliases}")
        converted = []
        for k, v in aliases.items():
            if isinstance(v, str):
                v_tuple = (v,)
            elif isinstance(v, (list, tuple)):
                v_tuple = tuple(v)
            else:
                raise TypeError(f"Type alias value must be str or list/tuple of str, got {type(v)}")
            converted.append((k, v_tuple))
        values["type_aliases"] = frozenset(converted)

        allowed_types: Any = values.get("allowed_types", tuple())
        values["allowed_types"] = tuple(allowed_types) if allowed_types is not None else tuple()
        return values

    @property
    def type_aliases_dict(self) -> Dict[str, List[str]]:
        """Return a normal dict[str, list[str]] for convenience."""
        return {k: list(v) for k, v in self.type_aliases}

    # -----------------------------
    # Factory / creation methods
    # -----------------------------
    @classmethod
    def _parse_config(cls: Type[T], config: Dict[str, Any]) -> T:
        if not isinstance(config, dict):
            raise ValueError(f"Expected a dict, got {type(config).__name__}")
        return cls.create(**config)

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """
        Factory to create the correct SchemaParserSettings subclass based on ContentType.

        Additional kwargs can be added without breaking this API.
        """
        kind = kwargs.pop("kind", None)
        if kind is not None:
            if isinstance(kind, str):
                try:
                    kind = ContentType(kind.lower())
                except ValueError:
                    raise ValueError(f"Invalid kind: {kind!r}")
            subclass = cls._KIND_MAP.get(kind)
            if subclass is None:
                raise ValueError(f"No SchemaParserSettings registered for kind {kind!r}")
            target_cls = subclass
        else:
            if cls is SchemaParserSettings:
                raise ValueError(f"Missing kind field for concrete class dispacth")
            target_cls = cls

        try:
            return cast(T, target_cls.model_validate(kwargs))
        except ValidationError as e:
            raise ValueError(f"Invalid fields for {target_cls.__name__}: {e}") from e


class YamlSchemaParserSettings(SchemaParserSettings):
    @property
    @overrides
    def kind(self) -> ContentType:
        return ContentType.YAML


# Register the YAML subclass
SchemaParserSettings.register_kind(ContentType.YAML, YamlSchemaParserSettings)
