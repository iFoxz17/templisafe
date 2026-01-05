import pytest
from pydantic import ValidationError
from sqltemplater.util.util import DiagnosticPolicy
from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings

def test_initialization():
    settings = YamlSchemaParserSettings(
        schema_key="schema",
        type_key="type",
        default_key="default",
    )
    assert settings.schema_key == "schema"
    assert settings.type_key == "type"
    assert settings.default_key == "default"
    assert settings.allowed_types == tuple()
    assert settings.type_aliases_dict == {}
    assert settings.policy is None

def test_initialization_with_values():
    policy = DiagnosticPolicy.ERRORS_ONLY
    settings = YamlSchemaParserSettings(
        schema_key="s",
        type_key="t",
        default_key="d",
        allowed_types=["int", "str"],           # type: ignore
        type_aliases={"int": ["integer"]},      # type: ignore
        policy=policy
    )
    assert settings.allowed_types == ("int", "str")
    assert settings.type_aliases_dict == {"int": ["integer"]}
    assert settings.policy == policy

def test_immutable():
    settings = YamlSchemaParserSettings(
        schema_key="s",
        type_key="t",
        default_key="d"
    )
    with pytest.raises(Exception):
        settings.schema_key = "new_value"

def test_validation_error():
    # Example: passing wrong type
    with pytest.raises(ValidationError):
        YamlSchemaParserSettings(
            schema_key=123,  # type: ignore     
            type_key="t",
            default_key="d"
        )
