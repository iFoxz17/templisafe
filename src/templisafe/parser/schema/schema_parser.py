from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from types import MappingProxyType
from typing import Annotated, Any, ClassVar, Iterable

from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from templisafe.core.metadata import Metadata, MetaValue
from templisafe.exceptions.schema_error import (
    IllegalSchemaError,
    IllegalType,
    IllegalVarDefault,
    IllegalVarType,
)
from templisafe.parser.config.config_parser import Config
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.template.template_model import Schema

PYDANTIC_METADATA_KEYS: frozenset[str] = frozenset({"title", "description", "example", "examples", "alias"})
_NO_DEFAULT: object = object()


class TypeParser:
    """Parses type strings into Python/Pydantic types, including composite type as nested lists, dicts and optionals."""

    __slots__: tuple[str, ...] = ("_allowed", "_aliases")

    _BASE_TYPE_MAP: ClassVar[MappingProxyType[str, Any]] = MappingProxyType(
        {
            "bool": bool,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "date": date,
            "datetime": datetime,
            "object": object,
        }
    )

    def __init__(self, allowed: Iterable[str], aliases: dict[str, str] | None = None) -> None:
        self._allowed: set[str] = set(allowed)
        self._aliases: dict[str, str] = aliases or {}

    @staticmethod
    def _is_list(type_name: str) -> bool:
        return type_name.startswith("list[") and type_name.endswith("]")

    def _parse_list(self, type_name: str) -> Any:
        inner_type_name: str = type_name[5:-1].strip()
        inner_type: Any = self.parse(inner_type_name)
        return list.__class_getitem__(inner_type)

    @staticmethod
    def _is_optional(type_name: str) -> bool:
        return type_name.startswith("optional[") and type_name.endswith("]")

    def _parse_optional(self, type_name: str) -> Any:
        inner_type_name: str = type_name[9:-1].strip()
        inner_type: Any = self.parse(inner_type_name)
        return inner_type | None

    @staticmethod
    def _is_dict(type_name: str) -> bool:
        return type_name.startswith("dict[") and type_name.endswith("]")

    @staticmethod
    def _split_dict_args(type_name: str, inner_content: str) -> tuple[str, str]:
        depth = 0
        for index, char in enumerate(inner_content):
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
            elif char == "," and depth == 0:
                return inner_content[:index].strip(), inner_content[index + 1 :].strip()
        raise ValueError(type_name)

    def _parse_dict(self, type_name: str) -> Any:
        inner_content: str = type_name[5:-1].strip()
        try:
            key_type_name, value_type_name = self._split_dict_args(type_name, inner_content)
        except ValueError as e:
            raise IllegalType(type_name, self._allowed, aliases=list(self._aliases.keys()))
        if not key_type_name or not value_type_name:
            raise IllegalType(type_name, self._allowed, aliases=list(self._aliases.keys()))
        key_type: Any = self.parse(key_type_name)
        value_type: Any = self.parse(value_type_name)
        return dict.__class_getitem__((key_type, value_type))

    def _normalize(self, type_name: str) -> str:
        type_name = type_name.strip()
        main_type_name = type_name[: type_name.find("[")].strip() if "[" in type_name else type_name
        sub_typing_name = type_name[type_name.find("[") :].strip() if "[" in type_name else ""
        return self._aliases.get(main_type_name, main_type_name) + sub_typing_name

    def parse(self, type_name: str) -> Any:
        """
        Parse a type annotation string into a corresponding Python type, supporting nested and generic types.

        This method handles the following constructs recursively:
        - `list[T]`        → Python `list` containing elements of type `T`
        - `optional[T]`    → Python `Optional[T]` (or `Union[T, None]`)
        - `dict[K, V]`     → Python `dict` with keys of type `K` and values of type `V`
        - Base types       → Python built-in types (int, str, bool, etc.), including any defined aliases

        Parameters
        ----------
        type_name : str
            The type string to parse. Can include nested generic types, e.g., `list[optional[int]]`.

        Returns
        -------
        type
            The corresponding Python type object for the given type string.

        Raises
        ------
        IllegalType
            If the `type_name` is not in the allowed base types or contains an unknown alias.
        """

        type_name = self._normalize(type_name)
        main_type_name = type_name[: type_name.find("[")].strip() if "[" in type_name else type_name
        if main_type_name not in self._allowed:
            raise IllegalType(type_name, self._allowed, aliases=list(self._aliases.keys()))

        if self._is_list(type_name):
            return self._parse_list(type_name)
        if self._is_optional(type_name):
            return self._parse_optional(type_name)
        if self._is_dict(type_name):
            return self._parse_dict(type_name)

        return self._BASE_TYPE_MAP[type_name]


@dataclass(frozen=True, slots=True)
class RawVar:
    """Represents a raw variable definition after configuration-key normalization."""

    type_str: str
    default: Any
    constraints: dict[str, Any]
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Var:
    """Represents a variable defined in the schema of the template."""

    index_: int
    name: str
    type_: Any
    default: Any
    constraints: dict[str, Any]
    field_metadata: dict[str, Any]
    pydantic_metadata: dict[str, Any]
    metadata: Metadata

    @property
    def has_default(self) -> bool:
        return self.default is not _NO_DEFAULT

    @property
    def field_default(self) -> Any:
        return self.default if self.has_default else ...

    @property
    def annotation(self) -> Any:
        return Annotated[self.type_, self.metadata]

    def field(self) -> Any:
        field_kwargs: dict[str, Any] = {
            **self.constraints,
            **self.pydantic_metadata,
        }
        return Field(self.field_default, **field_kwargs)


class SchemaParser:
    """Parses raw schema definitions into dynamic Pydantic models."""

    __slots__: tuple[str, ...] = ("_settings", "_type_parser")

    def __init__(self, settings: SchemaParserSettings) -> None:
        self._settings: SchemaParserSettings = settings
        aliases: dict[str, str] = {alias: t for t, al in settings.type_aliases for alias in al}
        self._type_parser = TypeParser(settings.allowed_types, aliases)

    def _parse_raw_var(self, name: str, schema: Any) -> RawVar:
        """Parse one raw variable definition into primitive pieces."""
        if isinstance(schema, str):
            return RawVar(type_str=schema, default=_NO_DEFAULT, constraints={}, metadata={})

        if not isinstance(schema, dict):
            raise IllegalSchemaError(f"Variable '{name}' has invalid schema: {schema}")

        return self._parse_raw_var_mapping(name, schema)

    def _parse_raw_var_mapping(self, name: str, schema: dict[str, Any]) -> RawVar:
        """Parse the verbose mapping form for a variable definition."""
        settings = self._settings
        if settings.type_key not in schema:
            raise IllegalSchemaError(f"Variable '{name}' is missing '{settings.type_key}' key")

        type_str = self._parse_raw_var_type(name, schema)
        default = schema[settings.default_key] if settings.default_key in schema else _NO_DEFAULT
        constraints = self._parse_raw_var_constraints(name, schema)
        metadata = self._parse_raw_var_metadata(name, schema)

        return RawVar(type_str=type_str, default=default, constraints=constraints, metadata=metadata)

    def _parse_raw_var_type(self, name: str, schema: dict[str, Any]) -> str:
        """Extract and validate the configured type string for a variable."""
        type_str = schema[self._settings.type_key]
        if not isinstance(type_str, str):
            raise IllegalSchemaError(f"Variable '{name}' has invalid type: {type_str}")
        return type_str

    def _parse_raw_var_constraints(self, name: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Extract and validate field constraints for a variable."""
        constraints = schema.get(self._settings.constraints_key, {})
        if not isinstance(constraints, dict):
            raise IllegalSchemaError(f"Variable '{name}' has invalid constraints: {constraints}")
        return constraints

    def _parse_raw_var_metadata(self, name: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Extract and validate user metadata for a variable."""
        metadata = schema.get(self._settings.metadata_key, {})
        if not isinstance(metadata, dict):
            raise IllegalSchemaError(f"Variable '{name}' has invalid metadata: {metadata}")
        return metadata

    def _parse_type(self, index: int, name: str, type_str: str) -> Any:
        try:
            return self._type_parser.parse(type_str)
        except IllegalType as e:
            raise IllegalVarType(
                index,
                name,
                type_str,
                list(self._type_parser._allowed | set(self._type_parser._aliases.keys())),
            ) from e

    def _validate_metadata(self, name: str, metadata: dict[str, Any]) -> None:
        """Reject user metadata that would override parser-owned entries."""
        if self._settings.index_key in metadata:
            raise IllegalSchemaError(
                f"Variable '{name}' metadata contains reserved keyword '{self._settings.index_key}'"
            )

    def _extract_pydantic_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Extract fields from the metadata dictionary that are recognized by Pydantic."""

        return {key: value for key, value in metadata.items() if key in PYDANTIC_METADATA_KEYS}

    def _create_field_metadata(self, index: int, metadata: dict[str, Any]) -> dict[str, Any]:
        """Return metadata stored in Pydantic's json schema extra map."""
        return {
            **{key: value for key, value in metadata.items() if key not in PYDANTIC_METADATA_KEYS},
            self._settings.index_key: index,
        }

    def _create_annotation_metadata(self, field_metadata: dict[str, Any]) -> Metadata:
        """Return rich metadata attached to the generated model field annotation."""
        return Metadata(
            {
                key: MetaValue(value=value, description="Schema parser field metadata")
                for key, value in field_metadata.items()
            }
        )

    def _parse_var(self, index: int, name: str, schema: Any) -> Var:
        """Parse a single variable definition into a `Var`."""
        raw_var = self._parse_raw_var(name, schema)
        type_ = self._parse_type(index, name, raw_var.type_str)
        self._validate_metadata(name, raw_var.metadata)
        field_metadata = self._create_field_metadata(index, raw_var.metadata)

        return Var(
            index_=index,
            name=name,
            type_=type_,
            default=raw_var.default,
            constraints=raw_var.constraints,
            field_metadata=field_metadata,
            pydantic_metadata=self._extract_pydantic_metadata(raw_var.metadata),
            metadata=self._create_annotation_metadata(field_metadata),
        )

    def _validate_default(self, var: Var) -> None:
        """Validate the default of a `Var` by instantiating a temporary Pydantic model."""

        if not var.has_default:
            return

        field_definitions: dict[str, Any] = {var.name: (var.type_, Field(var.default))}
        TempModel = create_model(
            "TempModel",
            __config__=ConfigDict(validate_default=True),
            **field_definitions,
        )

        try:
            TempModel()
        except ValidationError as e:
            raise IllegalVarDefault(
                var_index=var.index_,
                var_name=var.name,
                var_type=var.type_,
                var_default=var.default,
            ) from e

    def _parse_schema(self, schema_config: dict[str, Any]) -> Schema:
        """Convert a schema configuration into a Pydantic `BaseModel` type."""

        settings: SchemaParserSettings = self._settings
        schema_key: str = settings.schema_key

        if schema_key not in schema_config:
            raise IllegalSchemaError(f"Missing top-level schema key '{schema_key}'")

        vars_dict: dict[str, Any] = schema_config[schema_key]
        if not isinstance(vars_dict, dict):
            raise IllegalSchemaError(f"Expected the schema definition to be a dict, found: {vars_dict}")

        fields: dict[str, Any] = {}
        for i, (v_name, v_schema) in enumerate(vars_dict.items()):
            if not isinstance(v_name, str):
                raise IllegalSchemaError(f"Variable name at index {i} is not a string: '{v_name}'")

            var: Var = self._parse_var(i, v_name, v_schema)
            self._validate_default(var=var)
            fields[var.name] = (var.annotation, var.field())

        model_name: str = settings.model_name
        ModelSchema = create_model(
            model_name,
            __base__=BaseModel,
            __config__=ConfigDict(validate_default=True),
            **fields,
        )

        return Schema(model_cls=ModelSchema)

    def parse(self, schema_config: Config) -> Schema:
        """
        Parse a schema configuration dictionary into a `Schema`.

        Parameters
        ----------
        schema_config : Config
            The schema configuration. Must be a dictionary.

        Returns
        -------
        Schema
            A container for the dynamically created Pydantic model class
            corresponding to the provided schema.

        Raises
        ------
        SchemaError
            If the provided configuration cannot be parsed to a `Schema`.
        """

        if not isinstance(schema_config, dict):
            raise IllegalSchemaError(f"Expected schema configuration to be a dict, found: {schema_config}")

        return self._parse_schema(schema_config)
