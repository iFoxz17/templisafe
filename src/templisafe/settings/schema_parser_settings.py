from abc import ABC
from typing import Any, TypeVar

from pydantic import Field, model_validator

from templisafe.core.collections import dict_to_frozenset
from templisafe.settings.settings import Settings, SettingsKind

T = TypeVar("T", bound="SchemaParserSettings")


class SchemaParserSettings(Settings, ABC):
    """Settings class for defining schema parsers."""

    schema_key: str = Field("schema", description="The top-level key in the schema configuration")
    type_key: str = Field("type", description="The key for variable types in the schema configuration")
    default_key: str = Field(
        "default",
        description="The key for variable defaults in the schema configuration",
    )
    constraints_key: str = Field(
        "constraints",
        description="The key for variable constraints in the schema configuration",
    )
    metadata_key: str = Field(
        "metadata",
        description="The key for variable metadata in the schema configuration",
    )
    index_key: str = Field(
        "_index",
        description="The reserved key used to store variable indexes in the Pydantic model metadata",
    )
    model_name: str = Field(
        "ModelSchema",
        description="The name of the dynamic Pydantic model representing the schema",
    )
    allowed_types: tuple[str, ...] = Field(default_factory=tuple, description="The variable types allowed")
    type_aliases: frozenset[tuple[str, tuple[str, ...]]] = Field(
        default_factory=frozenset,
        description="The aliases for variable types in an hashable format",
    )

    @model_validator(mode="before")
    def convert_type_aliases(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Convert user-provided dict to frozenset automatically."""

        aliases: Any = values.get("type_aliases", {})
        if not isinstance(aliases, dict):
            raise TypeError(f"aliases must be a dict, got {aliases}")
        values["type_aliases"] = dict_to_frozenset(aliases)

        allowed_types: Any = values.get("allowed_types", tuple())
        values["allowed_types"] = tuple(allowed_types) if allowed_types is not None else tuple()
        return values

    @property
    def type_aliases_dict(self) -> dict[str, list[str]]:
        """Return a normal dict[str, list[str]] for convenience."""
        return {k: list(v) for k, v in self.type_aliases}


Settings.register_kind(SettingsKind.SCHEMA_PARSER_SETTINGS, SchemaParserSettings)
