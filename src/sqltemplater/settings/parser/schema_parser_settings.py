from abc import ABC
from overrides import overrides
from typing import Dict, List, Tuple, Any
from pydantic import Field, model_validator

from sqltemplater.util.util import ContentType
from sqltemplater.settings.parser.parser_settings import ParserSettings

class SchemaParserSettings(ParserSettings, ABC):
    schema_key: str
    type_key: str
    default_key: str
    allowed_types: Tuple[str, ...] = Field(default_factory=tuple)
    type_aliases: frozenset[tuple[str, tuple[str]]] = Field(default_factory=frozenset)

    model_config = {
        "frozen": True
    }

    @model_validator(mode="before")
    def convert_type_aliases(cls, values: Dict[str, Any]):
        """Convert user-provided dict to frozenset automatically."""
        aliases: Any = values.get("type_aliases", {})
        if isinstance(aliases, dict):
            # Convert dict[str, list[str]] -> frozenset[tuple[str, tuple[str]]]
            values["type_aliases"] = frozenset(
                (k, tuple(v)) for k, v in aliases.items()
            )

        allowed_types: Any = values.get("allowed_types", tuple())
        if isinstance(allowed_types, tuple):
            values["allowed_types"] = tuple(allowed_types)

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

