import pytest
from pydantic import BaseModel, ValidationError
from templisafe.exceptions.schema_error import (
    IllegalSchemaError,
    IllegalVarType,
    IllegalVarDefault
)
from templisafe.loader.schema.schema_parser import SchemaParser
from templisafe.settings.schema_parser_settings import SchemaParserSettings


@pytest.fixture
def settings() -> SchemaParserSettings:
    return SchemaParserSettings(
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
    parser = SchemaParser(settings)
    schema_config = {
        "parameters": {
            "age": {"type": "int", "default": 30},
            "name": "str"
        }
    }
    qschema = parser.parse(schema_config)
    model_cls = qschema.model_cls
    assert issubclass(model_cls, BaseModel)

    instance = model_cls(name="Alice")
    assert getattr(instance, "age") == 30
    assert getattr(instance, "name") == "Alice"
    model_fields = getattr(model_cls, "model_fields")
    age = model_fields["age"]
    age_metadata = getattr(age, "json_schema_extra")
    assert age_metadata['_index'] == 0
    name = model_fields["name"]
    name_metadata = getattr(name, "json_schema_extra")
    assert name_metadata['_index'] == 1


def test_parse_optional_field(settings):
    parser = SchemaParser(settings)
    schema_config = {"parameters": {"nickname": {"type": "optional[str]"}}}
    qschema = parser.parse(schema_config)
    model_cls = qschema.model_cls
    instance = model_cls(nickname=None)
    assert getattr(instance, "nickname") is None
    model_fields = getattr(model_cls, "model_fields")
    nickname = model_fields["nickname"]
    nickname_metadata = getattr(nickname, "json_schema_extra")
    assert nickname_metadata['_index'] == 0
    

def test_parse_list_field(settings):
    parser = SchemaParser(settings)
    schema_config = {"parameters": {"scores": {"type": "list[int]"}}}
    qschema = parser.parse(schema_config)
    model_cls = qschema.model_cls
    instance = model_cls(scores=[10, 20, 30])
    assert getattr(instance, "scores") == [10, 20, 30]
    model_fields = getattr(model_cls, "model_fields")
    scores = model_fields["scores"]
    scores_metadata = getattr(scores, "json_schema_extra")
    assert scores_metadata['_index'] == 0
    

def test_parse_with_alias(settings):
    parser = SchemaParser(settings)
    schema_config = {
        "parameters": {
            "quantity": "integer",
            "nickname": "string",
            "threshold": "real"
        }
    }
    qschema = parser.parse(schema_config)
    model_cls = qschema.model_cls
    instance = model_cls(quantity=42, nickname="volpemat01", threshold=1.345)
    model_fields = getattr(model_cls, "model_fields")
    assert getattr(instance, "quantity") == 42
    quantity = model_fields["quantity"]
    quantity_metadata = getattr(quantity, "json_schema_extra")
    assert quantity_metadata['_index'] == 0
    assert getattr(instance, "nickname") == "volpemat01"
    nickname = model_fields["nickname"]
    nickname_metadata = getattr(nickname, "json_schema_extra")
    assert nickname_metadata['_index'] == 1
    assert getattr(instance, "threshold") == 1.345
    threshold = model_fields["threshold"]
    threshold_metadata = getattr(threshold, "json_schema_extra")
    assert threshold_metadata['_index'] == 2
    

def test_parse_nested_list_optional(settings):
    parser = SchemaParser(settings)
    schema_config = {"parameters": {"matrix": {"type": "list[list[optional[str]]]"}}}
    qschema = parser.parse(schema_config)
    model_cls = qschema.model_cls
    instance = model_cls(matrix=[["a", None], ["b", "c"]])
    assert getattr(instance, "matrix") == [["a", None], ["b", "c"]]

    with pytest.raises(ValidationError):
        model_cls(matrix=[["a", 1]])


def test_parse_with_constraints_and_metadata(settings):
    parser = SchemaParser(settings)
    schema_config = {
        "parameters": {
            "score": {
                "type": "int",
                "constraints": {"gt": 0, "lt": 101},
                "metadata": {"description": "score of the query", "custom": "custom metadata"}
            },
            "name": {
                "type": "str",
                "constraints": {"max_length": 5},
                "metadata": {"examples": ["Mattia", "Andrea"], "title": "Name title", "tmp": "custom metadata"}
            }
        }
    }
    qschema = parser.parse(schema_config)
    model_cls = qschema.model_cls
    instance = model_cls(score=50, name="John")
    assert getattr(instance, "score") == 50
    assert getattr(instance, "name") == "John"
    score_field = model_cls.model_fields["score"]
    score_metadata = getattr(score_field, "json_schema_extra")
    assert score_metadata['_index'] == 0
    assert score_field.description == "score of the query"
    name_field = model_cls.model_fields["name"]
    name_metadata = getattr(name_field, "json_schema_extra")
    assert name_metadata['_index'] == 1
    assert name_field.examples == ["Mattia", "Andrea"]
    assert name_field.title == "Name title"
    assert name_metadata["tmp"] == "custom metadata"


def test_invalid_type_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"parameters": {"value": {"type": "unknown_type"}}}
    with pytest.raises(IllegalVarType):
        parser.parse(schema_config)


def test_wrong_default_type_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"parameters": {"quantity": {"type": "integer", "default": 1.3}}}
    with pytest.raises(IllegalVarDefault):
        parser.parse(schema_config)


def test_missing_schema_key_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"wrong_key": {"age": {"type": "int"}}}
    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)


def test_invalid_metadata_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"parameters": {"score": {"type": "int", "metadata": {"_index": 77}}}}
    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)
