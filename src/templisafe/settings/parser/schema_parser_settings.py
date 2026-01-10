from abc import ABC
from overrides import overrides
from typing import Dict, List, Tuple, Any
from pydantic import Field, model_validator

from templisafe.util.util import ContentType
from templisafe.settings.parser.parser_settings import ParserSettings

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
        """Return a normal dict[str, list[str]] for user convenience."""
        return {k: list(v) for k, v in self.type_aliases}
    
class YamlSchemaParserSettings(SchemaParserSettings):
    @property
    @overrides
    def content_type(self) -> ContentType:
        return ContentType.YAML

