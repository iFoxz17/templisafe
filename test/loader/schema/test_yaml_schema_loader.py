import pytest
import warnings
from numbers import Real
from sqltemplater.loader.schema.schema_parser import TypeParser, SchemaParser

from sqltemplater.loader.schema.yaml_schema_parser import YamlSchemaParser
from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings
from sqltemplater.template.template_model import Schema
from sqltemplater.util.util import DiagnosticPolicy
from sqltemplater.exceptions.schema_error import (
    IllegalType,
    IllegalSchemaError,
    IllegalVarType
)
from sqltemplater.exceptions.schema_warnings import DefaultVarTypeMismatchWarning

'''
# -----------------------
# TypeParser tests
# -----------------------
def test_type_parser_parse_and_validate():
    parser = TypeParser(allowed=["int", "str"], aliases={"integer": "int"})
    assert parser.validate("int")
    assert parser.validate("integer")
    assert parser.parse("int") is int
    assert parser.parse("integer") is int
    with pytest.raises(IllegalType):
        parser.parse("float")

def test_type_parser_parse_all():
    parser = TypeParser(
        allowed=["int", "str", "bool", "list", "real", "float", "object"], 
        aliases={"integer": "int", "number": "real", "boolean": "bool", "string": "str", "any": "object"})
    assert parser.parse("bool") is bool
    assert parser.parse("boolean") is bool
    assert parser.parse("int") is int
    assert parser.parse("integer") is int
    assert parser.parse("float") is float
    assert parser.parse("real") is Real
    assert parser.parse("number") is Real
    assert parser.parse("str") is str
    assert parser.parse("string") is str
    assert parser.parse("list") is list
    assert parser.parse("object") is object
    assert parser.parse("any") is object
    
    with pytest.raises(IllegalType):
        parser.parse("dummy")

def test_type_parser_allowed_with_aliases():
    parser = TypeParser(allowed=["int", "object"], aliases={"i": "int"})
    assert parser.allowed_with_aliases == {"int", "i", 'object'}

# -----------------------
# SchemaParser helper methods
# -----------------------
def test_reverse_aliases():
    aliases = frozenset([
        ("int", ("i", "integer")), 
        ("str", ("s",))
    ])
    reversed_aliases = QSchemaParser._reverse_aliases(aliases)
    assert reversed_aliases["i"] == "int"
    assert reversed_aliases["integer"] == "int"
    assert reversed_aliases["s"] == "str"
    
    # duplicate alias should raise
    with pytest.raises(IllegalSchemaError):
        QSchemaParser._reverse_aliases(
            frozenset([
                ("int", ("i",)), 
                ("str", ("i",))
                ])
        )

def test_parse_type_with_invalid_type():
    settings = YamlQSchemaParserSettings(schema_key="schema", type_key="type", default_key="default", allowed_types=("int",))
    class DummyParser(QSchemaParser):
        def _parse_raw(self, schema: str): return {}
    parser = DummyParser(settings)
    with pytest.raises(IllegalParamType):
        parser._parse_type(0, "p", "str")

def test_parse_short_and_complete():
    settings = YamlQSchemaParserSettings(schema_key="schema", type_key="type", default_key="default", allowed_types=("int",))
    class DummyParser(QSchemaParser):
        def _parse_raw(self, schema: str): return {}
    parser = DummyParser(settings)
    
    # _parse_short returns ParamSchema
    p = parser._parse_short(0, "x", "int")
    assert isinstance(p, QVar)
    assert p.index == 0 and p.name == "x" and p.type_ is int

    # _parse_complete with correct type
    schema_dict = {"type": "int", "default": 5}
    p2 = parser._parse_complete(0, "y", {"type": "int", "default": 5})
    assert p2.type_ is int
    assert p2.default == 5

def test_parse_complete_with_warning():
    settings = YamlQSchemaParserSettings(schema_key="schema", type_key="type", default_key="default",
                                    allowed_types=("int",), policy=DiagnosticPolicy.LOG_WARNINGS)
    class DummyParser(QSchemaParser):
        def _parse_raw(self, schema: str): return {}
    parser = DummyParser(settings)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        p = parser._parse_complete(0, "x", {"type": "int", "default": "wrong_type"})
        assert any(issubclass(warn.category, DefaultVarTypeMismatchWarning) for warn in w)

# -----------------------
# _parse_schema and parse
# -----------------------
def test_parse_schema():
    settings = YamlQSchemaParserSettings(schema_key="schema", type_key="type", default_key="default",
                                    allowed_types=("int",))
    class DummyParser(QSchemaParser):
        def _parse_raw(self, schema: str):
            return {
                "schema": {
                    "a": "int",
                    "b": {"type": "int"}
                }
            }
    parser = DummyParser(settings)
    qs = parser.parse("dummy")
    assert isinstance(qs, QSchema)
    assert set(qs.names) == {"a", "b"}

# -----------------------
# YamlSchemaParser
# -----------------------
def test_yaml_schema_parser_valid_and_invalid():
    settings = YamlQSchemaParserSettings(schema_key="schema", type_key="type", default_key="default",
                                    allowed_types=("int",))
    parser = QYamlSchemaParser(settings)
    
    valid_yaml = """
schema:
  a: int
  b:
    type: int
    default: 5
"""
    qs = parser.parse(valid_yaml)
    assert isinstance(qs, QSchema)
    assert set(qs.names) == {"a", "b"}

    invalid_yaml = "!!yaml invalid"
    with pytest.raises(IllegalSchemaError):
        parser.parse(invalid_yaml)

    non_dict_yaml = "- a\n- b"
    with pytest.raises(IllegalSchemaError):
        parser.parse(non_dict_yaml)
'''