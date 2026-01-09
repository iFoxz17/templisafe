import pytest
from pydantic import BaseModel
from sqltemplater.exceptions.schema_error import (
    IllegalSchemaError,
    IllegalVarType,
    IllegalVarDefault
)
from sqltemplater.loader.schema.yaml_schema_parser import YamlSchemaParser
from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings


@pytest.fixture
def settings() -> YamlSchemaParserSettings:
    return YamlSchemaParserSettings(
        schema_key="parameters",
        type_key="type",
        default_key="default",
        constraints_key="constraints",
        metadata_key="metadata",
        index_key="_index",
        model_name="TestModel",
        allowed_types=("int", "str", "float", "bool", "object"),
        type_aliases={"int": ["integer"], "str": ["string"], "float": ["real", "number"]},   # type: ignore
    )


def test_parse_simple_schema(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  age:
    type: int
    default: 30
  name: str
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls
    assert issubclass(model_cls, BaseModel)

    # Check defaults and type annotations
    instance = model_cls(name="Alice")
    assert getattr(instance, "age", None) == 30
    assert getattr(instance, "name", None) == "Alice"
    age_field = model_cls.model_fields["age"]
    assert age_field.json_schema_extra is not None
    assert age_field.json_schema_extra.get("_index") == 0        # type: ignore
    
    name_field = model_cls.model_fields["name"]
    assert name_field.json_schema_extra.get("_index") == 1       # type: ignore


def test_parse_optional_field(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  nickname:
    type: optional[str]
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls
    instance = model_cls(nickname=None)
    assert getattr(instance, "nickname", "volpemat01") is None
    nickname_field = model_cls.model_fields["nickname"]
    assert nickname_field.json_schema_extra.get("_index") == 0       # type: ignore


def test_parse_list_field(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  scores:
    type: list[int]
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls
    instance = model_cls(scores=[10, 20, 30])
    assert getattr(instance, "scores", None) == [10, 20, 30]
    scores_field = model_cls.model_fields["scores"]
    assert scores_field.json_schema_extra.get("_index") == 0       # type: ignore


def test_parse_union_field_raises(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  code:
    type: str | int
"""
    with pytest.raises(IllegalVarType):
      parser.parse(yaml_schema)
    

def test_parse_with_alias(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  quantity:
    type: integer
  nickname: string
  threshold: real
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls
    instance = model_cls(quantity=42, nickname="volpemat01", threshold=1.345)
    
    assert getattr(instance, "quantity", None) == 42
    quantity_field = model_cls.model_fields["quantity"]
    assert quantity_field.json_schema_extra.get("_index") == 0       # type: ignore

    assert getattr(instance, "nickname", None) == "volpemat01"
    nickname_field = model_cls.model_fields["nickname"]
    assert nickname_field.json_schema_extra.get("_index") == 1       # type: ignore

    assert getattr(instance, "threshold", None) == 1.345
    threshold_field = model_cls.model_fields["threshold"]
    assert threshold_field.json_schema_extra.get("_index") == 2       # type: ignore


def test_parse_with_default(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  quantity:
    type: integer
    default: 10

  generic:
    type: object
    default: generic
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls
    instance = model_cls()
    
    assert getattr(instance, "quantity", None) == 10
    quantity_field = model_cls.model_fields["quantity"]
    assert quantity_field.json_schema_extra.get("_index") == 0       # type: ignore
    
    assert getattr(instance, "generic", None) == "generic"
    quantity_field = model_cls.model_fields["generic"]
    assert quantity_field.json_schema_extra.get("_index") == 1       # type: ignore


def test_parse_nested_list_optional(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  matrix:
    type: list[list[optional[str]]]
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls

    # Accept valid nested lists with None
    instance = model_cls(matrix=[["a", None], ["b", "c"]])
    assert getattr(instance, "matrix") == [["a", None], ["b", "c"]]
    matrix_field = model_cls.model_fields["matrix"]
    assert matrix_field.json_schema_extra.get("_index") == 0       # type: ignore

    # Reject wrong type
    import pytest
    with pytest.raises(Exception):
        model_cls(matrix=[["a", 1]])  # inner list must be str | None


def test_parse_with_constraints_and_metadata(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  score:
    type: int
    constraints:
      gt: 0
      lt: 101
    metadata:
      description: score of the query
      custom: custom metadata field for score

  name:
    type: str
    constraints:
      max_length: 5
    metadata:
      examples: 
        - Mattia
        - Andrea
      title: Name title
      tmp: custom metadata field for name
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls

    # Valid values
    instance = model_cls(score=50, name="John")
    assert getattr(instance, "score", None) == 50
    score_field = model_cls.model_fields["score"]
    assert score_field.json_schema_extra.get("_index") == 0       # type: ignore
    
    assert "description" not in score_field.json_schema_extra     # type: ignore
    assert score_field.description == "score of the query"          

    assert score_field.json_schema_extra.get("custom") == "custom metadata field for score"       # type: ignore

    assert getattr(instance, "name") == "John"
    name_field = model_cls.model_fields["name"]
    assert name_field.json_schema_extra.get("_index") == 1        # type: ignore
    
    assert "examples" not in name_field.json_schema_extra         # type: ignore
    assert name_field.examples == ["Mattia", "Andrea"]
    assert "title" not in name_field.json_schema_extra            # type: ignore
    assert name_field.title == "Name title"
    
    assert name_field.json_schema_extra.get("tmp") == "custom metadata field for name"       # type: ignore

    # Invalid score
    import pytest
    with pytest.raises(Exception):
        model_cls(score=200, name="John")  # gt=0, lt=101

    # Invalid name
    with pytest.raises(Exception):
        model_cls(score=50, name="Jonathan")  # max_length=5


def test_parse_with_invalid_metadata_raises(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  score:
    type: int
    metadata:
      _index: 77
"""
    with pytest.raises(IllegalSchemaError):
        qschema = parser.parse(yaml_schema)


def test_invalid_yaml_raises(settings):
    parser = YamlSchemaParser(settings)
    invalid_yaml = "::: not a valid yaml :::"
    with pytest.raises(IllegalSchemaError):
        parser.parse(invalid_yaml)


def test_missing_schema_key_raises(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
wrong_key:
  age:
    type: int
"""
    with pytest.raises(IllegalSchemaError):
        parser.parse(yaml_schema)


def test_invalid_type_raises(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  value:
    type: unknown_type
"""
    with pytest.raises(IllegalVarType):
        parser.parse(yaml_schema)


def test_parse_wrong_default_type(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  quantity:
    type: integer
    default: 1.3
"""
    with pytest.raises(IllegalVarDefault):
        parser.parse(yaml_schema)

    yaml_schema = """
parameters:
  quantity:
    type: optional[str]
    default: 1.3
"""
    with pytest.raises(IllegalVarDefault):
        parser.parse(yaml_schema)

    yaml_schema = """
parameters:
  quantities:
    type: list[str]
    default: [1, "a", 5.4]
"""
    with pytest.raises(IllegalVarDefault):
        parser.parse(yaml_schema)

    yaml_schema = """
parameters:
  quantities:
    type: list[object]
    default: [1, "a", 5.4]
"""
    parser.parse(yaml_schema)


def test_duplicate_parameter(settings):
    parser = YamlSchemaParser(settings)
    yaml_schema = """
parameters:
  a:
    type: int
  a:
    type: str
"""
    qschema = parser.parse(yaml_schema)
    model_cls = qschema.model_cls
    instance = model_cls(a="a")
    assert getattr(instance, "a", None) == "a"
