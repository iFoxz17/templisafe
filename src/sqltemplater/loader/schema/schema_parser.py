from typing import Any, Iterable
from abc import ABC, abstractmethod
from numbers import Real

from sqltemplater.loader.parser import Parser
from sqltemplater.settings.parser.schema_parser_settings import SchemaParserSettings
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.query.query_model import QuerySchema, ParamSchema
from sqltemplater.exceptions.schema_error import (
    IllegalType,
    IllegalSchemaError, 
    IllegalParamType,
    DuplicatedParamError
)
from sqltemplater.exceptions.schema_warnings import DefaultParamTypeMismatchWarning

class TypeParser:
    __slots__ = ('_allowed', '_aliases')

    _TYPE_MAP: dict[str, type] = {
            'bool': bool,
            'int': int,
            'float': float,
            'real': Real,
            'str': str,
            'list': list,
            'object': object
        }
    
    def __init__(self, allowed: Iterable[str], aliases: dict[str, str] | None = None) -> None:
        self._allowed: set[str] = set(allowed)
        self._aliases: dict[str, str] = aliases or {}
    
    @property
    def allowed(self) -> set[str]:
        return self._allowed
    
    @property
    def aliases(self) -> dict[str ,str]:
        return self._aliases
    
    @property
    def allowed_with_aliases(self) -> set[str]:
        return self._allowed | set(self._aliases.keys())

    def parse(self, name: str) -> type:
        if name in self._aliases:
            name = self._aliases[name]
        elif name not in self._allowed:
            raise IllegalType(name, self._allowed, aliases=list(self._aliases.keys()))

        return TypeParser._TYPE_MAP[name]

    def validate(self, name: str) -> bool:
        return name in self._allowed or name in self._aliases

class SchemaParser(Parser, ABC):
    """
    Abstract base class for parsing and validating schemas.
    """

    __slots__ = ('_settings', '_type_parser')
    
    @staticmethod
    def _reverse_aliases(type_aliases: frozenset[tuple[str, tuple[str, ...]]]) -> dict[str, str]:
        aliases_map: dict[str, str] = {}
        for type_, aliases in type_aliases:
            for alias in aliases:
                if alias in aliases_map:
                    raise IllegalSchemaError(f'Illegal aliases definition: alias {alias} is declared twice')
                aliases_map[alias] = type_

        return aliases_map

    def __init__(self, settings: SchemaParserSettings) -> None:
        super().__init__(settings)
        self._type_parser: TypeParser = TypeParser(
            settings.allowed_types,
            SchemaParser._reverse_aliases(settings.type_aliases)
        )
       
    def _parse_type(self, p_index: int, p_name: str, p_type: str) -> type:
        parser: TypeParser = self._type_parser
        if not parser.validate(p_type):
            raise IllegalParamType(p_index, p_name, p_type, list(parser.allowed_with_aliases))
        
        return parser.parse(p_type)

    def _parse_short(self, p_index: int, p_name: str, p_type: str) -> ParamSchema:
        type_: type = self._type_parser.parse(p_type)
        return ParamSchema(index=p_index, name=p_name, type_=type_)

    def _parse_complete(self, p_index: int, p_name: str, p_schema: dict[str, Any]) -> ParamSchema:
        settings: ParserSettings = self._settings
        assert isinstance(settings, SchemaParserSettings)

        type_key: str = settings.type_key
        if type_key not in p_schema:
            raise IllegalSchemaError(f'Illegal definition of parameter {p_index}: missing {type_key} key')

        p_type: Any = p_schema[type_key]
        if not isinstance(p_type, str):
            raise IllegalSchemaError(f'Illegal definition of parameter {p_index} ({p_name}): {p_type} is not a valid type')
        type_: type = self._type_parser.parse(p_type)

        p_default: Any = p_schema.get(settings.default_key)
        if p_default is None:
            return ParamSchema(index=p_index, name=p_name, type_=type_)
        
        default_type: type = type(p_default)
        if default_type != type_:
            self._handle_warning(DefaultParamTypeMismatchWarning(p_index, p_name, type_, default_type))

        return ParamSchema(index=p_index, name=p_name, type_=type_, default=p_default)
            
    def _parse_schema(self, schema_dict: dict[str, Any]) -> QuerySchema:
        settings: ParserSettings = self._settings
        assert isinstance(settings, SchemaParserSettings)
        
        schema_key: str = settings.schema_key
        if schema_key not in schema_dict:
            raise IllegalSchemaError(f"Missing top-level schema key '{schema_key}'")
        
        params_dict: Any = schema_dict[schema_key]
        if not isinstance(params_dict, dict):
            raise IllegalSchemaError(f'Illegal schema definition')

        params: dict[str, ParamSchema] = {}
        param_schema: ParamSchema
        
        for i, (p_name, p_schema) in enumerate(params_dict.items()):
            if not isinstance(p_name, str):
                raise IllegalSchemaError(f'Illegal definition of parameter {i}: {p_name} is not a string')
            if isinstance(p_schema, dict):
                param_schema = self._parse_complete(i, p_name, p_schema)
            elif isinstance(p_schema, str):
                param_schema = self._parse_short(i, p_name, p_schema)
            else:
                raise IllegalSchemaError(f'Illegal definition of parameter {i} ({p_name}): invalid schema: {p_schema}')
            
            if p_name in params:        # This should never happen since dict cannot have duplicated keys
                raise DuplicatedParamError(p_name, params[p_name].index, i)
            params[p_name] = param_schema

        return QuerySchema(params.values())
    
    @abstractmethod
    def _parse_raw(self, schema: str) -> dict[str, Any]:
        pass

    def parse(self, schema: str) -> QuerySchema:
        return self._parse_schema(self._parse_raw(schema))
        
