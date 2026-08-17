from datetime import date, datetime

import pytest
from pydantic import BaseModel, ValidationError

from templisafe.core.metadata import Metadata
from templisafe.exceptions.schema_error import (
    IllegalSchemaError,
    IllegalVarDefault,
    IllegalVarType,
)
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.settings.schema_parser_settings import SchemaParserSettings


@pytest.fixture
def settings() -> SchemaParserSettings:
    return SchemaParserSettings(
        index_key="_index",
        model_name="TestModel",
        allowed_types=(
            "int",
            "str",
            "float",
            "bool",
            "optional",
            "list",
            "dict",
            "date",
            "datetime",
            "object",
        ),
        type_aliases={
            "int": ["integer"],
            "str": ["string"],
            "float": ["real", "number"],
            "list": ["tuple"],
            "dict": ["mapping"],
        },  # type: ignore
    )


def field_metadata(model_cls: type[BaseModel], field_name: str) -> Metadata:
    field = model_cls.model_fields[field_name]
    return next(meta for meta in field.metadata if isinstance(meta, Metadata))


def test_parse_simple_schema(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"age": {"type": "int", "default": 30}, "name": "str"}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    assert issubclass(model_cls, BaseModel)

    instance = model_cls(name="Alice")
    assert getattr(instance, "age") == 30
    assert getattr(instance, "name") == "Alice"
    model_fields = getattr(model_cls, "model_fields")
    assert model_fields["age"].json_schema_extra is None
    assert model_fields["name"].json_schema_extra is None
    assert field_metadata(model_cls, "age")["_index"].value == 0
    assert field_metadata(model_cls, "name")["_index"].value == 1


def test_parse_optional_field(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"nickname": {"type": "optional[str]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    instance = model_cls(nickname=None)
    assert getattr(instance, "nickname") is None
    assert model_cls.model_fields["nickname"].json_schema_extra is None
    assert field_metadata(model_cls, "nickname")["_index"].value == 0


def test_parse_optional_field_with_null_default_is_not_required(settings):
    parser = SchemaParser(settings)
    schema_config = {
        "schema": {
            "nickname": {
                "type": "optional[str]",
                "default": None,
            }
        }
    }

    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    instance = model_cls()

    assert getattr(instance, "nickname") is None
    assert model_cls.model_fields["nickname"].is_required() is False


def test_parse_list_field(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"scores": {"type": "list[int]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    instance = model_cls(scores=[10, 20, 30])
    assert getattr(instance, "scores") == [10, 20, 30]
    assert model_cls.model_fields["scores"].json_schema_extra is None
    assert field_metadata(model_cls, "scores")["_index"].value == 0


def test_parse_date_field(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"birth_date": {"type": "date"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls

    # Create instance with a valid date
    d = date(2000, 1, 1)
    instance = model_cls(birth_date=d)
    assert getattr(instance, "birth_date") == d

    assert model_cls.model_fields["birth_date"].json_schema_extra is None
    assert field_metadata(model_cls, "birth_date")["_index"].value == 0


def test_parse_datetime_field(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"event_time": {"type": "datetime"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls

    # Create instance with a valid datetime
    dt = datetime(2023, 1, 1, 12, 30, 0)
    instance = model_cls(event_time=dt)
    assert getattr(instance, "event_time") == dt

    assert model_cls.model_fields["event_time"].json_schema_extra is None
    assert field_metadata(model_cls, "event_time")["_index"].value == 0


def test_parse_nested_list_optional(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"matrix": {"type": "list[list[optional[str]]]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    instance = model_cls(matrix=[["a", None], ["b", "c"]])
    assert getattr(instance, "matrix") == [["a", None], ["b", "c"]]

    with pytest.raises(ValidationError):
        model_cls(matrix=[["a", 1]])


def test_parse_nested_dict(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"nested": {"type": "dict[str, list[dict[str, float]]]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    nested: dict = {"top": [{"field1": 1}, {"field2": 2.1}, {"field3": 3.2}]}
    instance = model_cls(nested=nested)
    assert getattr(instance, "nested") == nested


def test_parse_nested_object(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"nested": {"type": "object"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    nested: dict = {"top": [{"field1": "value1"}, {"field2": 2.1}, {"field3": True}]}
    instance = model_cls(nested=nested)
    assert getattr(instance, "nested") == nested


def test_parse_with_alias(settings):
    parser = SchemaParser(settings)
    schema_config = {
        "schema": {
            "quantity": "integer",
            "nickname": "string",
            "threshold": "real",
            "sequence": "tuple[mapping[int, int]]",
            "nested": "mapping[str, mapping[int, float]]",
        }
    }
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls

    nested = {"field": {1: 1.1234, 2: 2.5678}}
    sequence = [{1: 2}, {2: 3}, {3: 4}]

    instance = model_cls(
        quantity=42,
        nickname="volpemat01",
        threshold=1.345,
        sequence=sequence,
        nested=nested,
    )
    model_fields = getattr(model_cls, "model_fields")
    assert getattr(instance, "quantity") == 42
    assert model_fields["quantity"].json_schema_extra is None
    assert field_metadata(model_cls, "quantity")["_index"].value == 0
    assert getattr(instance, "nickname") == "volpemat01"
    assert model_fields["nickname"].json_schema_extra is None
    assert field_metadata(model_cls, "nickname")["_index"].value == 1
    assert getattr(instance, "threshold") == 1.345
    assert model_fields["threshold"].json_schema_extra is None
    assert field_metadata(model_cls, "threshold")["_index"].value == 2
    assert getattr(instance, "sequence") == sequence
    assert model_fields["sequence"].json_schema_extra is None
    assert field_metadata(model_cls, "sequence")["_index"].value == 3
    assert getattr(instance, "nested") == nested
    assert model_fields["nested"].json_schema_extra is None
    assert field_metadata(model_cls, "nested")["_index"].value == 4


def test_parse_with_constraints_and_metadata(settings):
    parser = SchemaParser(settings)
    schema_config = {
        "schema": {
            "score": {
                "type": "int",
                "constraints": {"gt": 0, "lt": 101},
                "metadata": {
                    "description": "score of the query",
                    "custom": "custom metadata",
                },
            },
            "name": {
                "type": "str",
                "constraints": {"max_length": 5},
                "metadata": {
                    "examples": ["Mattia", "Andrea"],
                    "title": "Name title",
                    "tmp": "custom metadata",
                },
            },
        }
    }
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    instance = model_cls(score=50, name="John")
    assert getattr(instance, "score") == 50
    assert getattr(instance, "name") == "John"
    score_field = model_cls.model_fields["score"]
    score_metadata = field_metadata(model_cls, "score")
    assert score_field.json_schema_extra is None
    assert score_metadata["_index"].value == 0
    assert score_metadata["custom"].value == "custom metadata"
    assert score_field.description == "score of the query"
    name_field = model_cls.model_fields["name"]
    name_metadata = field_metadata(model_cls, "name")
    assert name_field.json_schema_extra is None
    assert name_metadata["_index"].value == 1
    assert name_field.examples == ["Mattia", "Andrea"]
    assert name_field.title == "Name title"
    assert name_metadata["tmp"].value == "custom metadata"


def test_parse_with_alias_metadata(settings):
    parser = SchemaParser(settings)
    schema_config = {
        "schema": {
            "user_name": {
                "type": "str",
                "metadata": {
                    "alias": "userName",
                    "custom": "kept as schema metadata",
                },
            }
        }
    }

    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    instance = model_cls(userName="Ada")
    field = model_cls.model_fields["user_name"]
    metadata = field_metadata(model_cls, "user_name")

    assert getattr(instance, "user_name") == "Ada"
    assert field.alias == "userName"
    assert field.json_schema_extra is None
    assert metadata["_index"].value == 0
    assert metadata["custom"].value == "kept as schema metadata"


def test_schema_definition_must_be_a_dict(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": ["age", "name"]}

    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)


def test_variable_mapping_requires_type_key(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"age": {"default": 30}}}

    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)


def test_constraints_must_be_a_dict(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"age": {"type": "int", "constraints": ["gt", 0]}}}

    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)


def test_dict_type_requires_key_and_value_types(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"mapping": {"type": "dict[str]"}}}

    with pytest.raises(IllegalVarType):
        parser.parse(schema_config)


def test_invalid_optional_subtyping_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"value": {"type": "optional[int]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    with pytest.raises(ValidationError):
        _ = model_cls(value=2.1)


def test_invalid_list_subtyping_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"value": {"type": "list[object]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    _ = model_cls(value=[1, 2.2, True, "a"])

    schema_config = {"schema": {"value": {"type": "list[float]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    with pytest.raises(ValidationError):
        _ = model_cls(value=[1, 2.2, 3.3, "a"])


def test_invalid_dict_subtyping_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"value": {"type": "dict[object, object]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    _ = model_cls(value={"a": [{"b": 1}, {2: [1, "a", True], 3: False}, "a", 4], "h": 2.3})

    schema_config = {"schema": {"value": {"type": "dict[str, object]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    with pytest.raises(ValidationError):
        _ = model_cls(value={1: "test"})

    schema_config = {"schema": {"value": {"type": "dict[object, str]"}}}
    schema = parser.parse(schema_config)
    model_cls = schema.model_cls
    with pytest.raises(ValidationError):
        _ = model_cls(value={1: 1})


def test_invalid_type_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"value": {"type": "unknown_type"}}}
    with pytest.raises(IllegalVarType):
        parser.parse(schema_config)


def test_wrong_default_type_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"quantity": {"type": "integer", "default": 1.3}}}
    with pytest.raises(IllegalVarDefault):
        parser.parse(schema_config)


def test_schema_config_is_not_a_dict_raises(settings):
    parser = SchemaParser(settings)
    schema_config = [{"schema": {"a": "int"}}]
    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)  # type: ignore


def test_missing_schema_key_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"wrong_key": {"age": {"type": "int"}}}
    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)


def test_invalid_metadata_raises(settings):
    parser = SchemaParser(settings)
    schema_config = {"schema": {"score": {"type": "int", "metadata": {"_index": 77}}}}
    with pytest.raises(IllegalSchemaError):
        parser.parse(schema_config)
