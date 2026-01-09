from abc import ABC, abstractmethod
from typing import Any, Union, Iterable, NamedTuple
from types import MappingProxyType
from datetime import date, datetime
from pydantic import BaseModel, ValidationError, Field 

from sqltemplater.template.template_model import Schema
from sqltemplater.settings.parser.schema_parser_settings import SchemaParserSettings
from sqltemplater.exceptions.schema_error import (
    IllegalType,
    IllegalSchemaError,
    IllegalVarType,
    IllegalVarDefault
)

class TypeParser:
    """Parses type strings into Python/Pydantic types, including nested list and optional types."""

    _BASE_TYPE_MAP: MappingProxyType[str, type] = MappingProxyType({
        "bool": bool,
        "int": int,
        "float": float,
        "str": str,
        "list": list,
        "date": date,
        "datetime": datetime,
        "object": object,
    })

    def __init__(self, allowed: Iterable[str], aliases: dict[str, str] | None = None) -> None:
        self._allowed: set[str] = set(allowed)
        self._aliases: dict[str, str] = aliases or {}

    def parse(self, type_name: str) -> type:
        """Parse type string into Python type, recursively handling list[...] and optional[...]"""
        type_name = type_name.strip()

        # Resolve aliases
        if type_name in self._aliases:
            type_name = self._aliases[type_name]

        # Handle list[T]
        if type_name.startswith("list[") and type_name.endswith("]"):
            inner_type_name: str = type_name[5:-1].strip()
            inner_type: type = self.parse(inner_type_name)
            return list[inner_type]

        # Handle optional[T]
        if type_name.startswith("optional[") and type_name.endswith("]"):
            inner_type_name: str = type_name[9:-1].strip()
            inner_type: type = self.parse(inner_type_name)
            return Union[inner_type, None]          # type: ignore

        # Base type
        if type_name not in self._allowed:
            raise IllegalType(type_name, self._allowed, aliases=list(self._aliases.keys()))
        return self._BASE_TYPE_MAP[type_name]


class Var(NamedTuple):
    index_: int
    name: str
    type_: type
    default: object
    constraints: dict[str, object]
    metadata: dict[str, object]


class SchemaParser(ABC):
    """Parses raw schema definitions into dynamic Pydantic models."""

    __slots__: tuple[str, ...] = ("_settings", "_type_parser")

    def __init__(self, settings: SchemaParserSettings) -> None:
        self._settings: SchemaParserSettings = settings
        aliases: dict[str, str] = {alias: t for t, al in settings.type_aliases for alias in al}
        self._type_parser = TypeParser(settings.allowed_types, aliases)

    @abstractmethod
    def _parse_raw(self, schema: str) -> dict[str, Any]:
        """Convert a raw schema string into a Python dictionary."""
        pass

    def _parse_var(self, index: int, name: str, schema: Any) -> Var:
        """Parse a single variable data and metadata into a Var."""

        settings: SchemaParserSettings = self._settings
        type_key: str = settings.type_key
        default_key: str = settings.default_key
        constraints_key: str = settings.constraints_key
        metadata_key: str = settings.metadata_key

        if isinstance(schema, str):
            type_str = schema
            default = None
            constraints: dict[str, Any] = {}
            metadata: dict[str, Any] = {}
        elif isinstance(schema, dict):
            if type_key not in schema:
                raise IllegalSchemaError(f"Variable '{name}' missing '{type_key}' key")
            type_str = schema[type_key]
            default = schema.get(default_key)
            constraints = schema.get(constraints_key, {})
            if not isinstance(constraints, dict):
                raise IllegalSchemaError(
                    f"Variable '{name}' has invalid constraints: {constraints}"
                )
            metadata = schema.get(metadata_key, {})
            if not isinstance(metadata, dict):
                raise IllegalSchemaError(
                    f"Variable '{name}' has invalid metadata: {metadata}"
                )
        else:
            raise IllegalSchemaError(f"Variable '{name}' has invalid schema: {schema}")

        try:
            type_: type = self._type_parser.parse(type_str)
        except IllegalType as e:
            raise IllegalVarType(
                index,
                name,
                type_str,
                list(self._type_parser._allowed | set(self._type_parser._aliases.keys())),
            ) from e

        return Var(
            index_=index,
            name=name,
            type_=type_,
            default=default,
            constraints=constraints,
            metadata=metadata
        )
    
    def _add_internal_metadata(self, metadata: dict[str, Any], var: Var) -> None:
        """Inject internal metadata fields required by the parser."""

        index_key: str = self._settings.index_key
        if index_key in metadata:
            raise IllegalSchemaError(f"Variable '{var.name}' metadata contains reserved keyword '{index_key}'")
        metadata[index_key] = var.index_

    def _extract_pydantic_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Extract fields from the metadata dictionary that are recognized by Pydantic."""
        
        return {
            k: metadata.pop(k) 
            for k in ["title", "description", "example", "examples", "alias"]
            if k in metadata
        }
    
    def _validate_default(self, var: Var) -> None:
        """Validate the default of a Var by instanting a temporary Pydantic model."""

        default: Any = var.default
        if default is None:
            return  # skip required fields
        
        # Prepare namespace with type annotation and Field instance
        namespace: dict[str, Any] = {
            '__annotations__': {var.name: var.type_},          # type hint
            'model_config': {'validate_default': True},        # abilitate default values validation
            var.name: Field(default)                   # default value
        }
        TempModel: type[BaseModel] = type('TempModel', (BaseModel,), namespace)
        
        # Instantiating TempModel will validate the default value
        try:
            TempModel()
        except ValidationError as e:
            raise IllegalVarDefault(
                var_index=var.index_,
                var_name=var.name,
                var_type=var.type_,
                var_default=var.default
            ) from e

    def _parse_schema(self, schema_dict: dict[str, Any]) -> Schema:
        """Convert a schema dictionary into a Pydantic BaseModel type."""

        settings: SchemaParserSettings = self._settings
        schema_key : str = settings.schema_key

        if schema_key not in schema_dict:
            raise IllegalSchemaError(f"Missing top-level schema key '{schema_key}'")

        vars_dict: dict[str, Any] = schema_dict[schema_key]
        if not isinstance(vars_dict, dict):
            raise IllegalSchemaError(f"Top-level schema must be a dict: {vars_dict}")

        fields: dict[str, Any] = {}
        for i, (v_name, v_schema) in enumerate(vars_dict.items()):
            if not isinstance(v_name, str):
                raise IllegalSchemaError(f"Variable name at index {i} is not a string: {v_name}")

            # v_name cannot be duplicated since it is the key of a dict
            var: Var = self._parse_var(i, v_name, v_schema)
            self._validate_default(var=var)

            # Extract metadata
            metadata: dict[str, Any] = var.metadata
            self._add_internal_metadata(metadata, var)
            pydantic_metadata: dict[str, Any] = self._extract_pydantic_metadata(metadata)

            # Create field with default validation
            fields[var.name] = (
                var.type_,
                Field(
                    var.default if var.default is not None else ...,
                    **var.constraints,
                    **pydantic_metadata,
                    json_schema_extra=metadata
                )
            )

        model_name: str = settings.model_name

        # Create the Pydantic model with default validation enabled
        ModelSchema: type[BaseModel] = type(
            model_name,
            (BaseModel,),
            {
                '__annotations__': {name: t for name, (t, _) in fields.items()},
                **{name: f for name, (_, f) in fields.items()},
                'model_config': {'validate_default': True}  # Pydantic v2 default type validation
            }
        )

        return Schema(model_cls=ModelSchema)


    def parse(self, schema: str) -> Schema:
        """Parse raw schema string into a dynamic Pydantic model type."""
        raw_dict = self._parse_raw(schema)
        return self._parse_schema(raw_dict)
