import json

import pytest
import yaml

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.schema_parser_settings import SchemaParserSettings, Settings

# ---------------------------------------------------------------------------
# Sample configuration data
# ---------------------------------------------------------------------------
MINIMAL_CONFIG = {
    "index_key": "index",
    "model_name": "MyModel",
}

FULL_CONFIG = {
    **MINIMAL_CONFIG,
    "allowed_types": ["int", "str"],
    "type_aliases": {
        "number": ["int", "float"],
        "text": "str",
    },
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_create_base_defaults():
    settings = Settings.create(kind="schema_parser_settings")
    assert isinstance(settings, SchemaParserSettings)
    assert settings.index_key == "_index"
    assert settings.model_name == "ModelSchema"
    assert settings.allowed_types == ()
    assert settings.type_aliases == frozenset()


def test_create_base_minimal():
    settings = Settings.create(kind="schema_parser_settings", **MINIMAL_CONFIG)
    assert isinstance(settings, SchemaParserSettings)
    assert settings.index_key == "index"
    assert settings.model_name == "MyModel"
    assert settings.allowed_types == ()
    assert settings.type_aliases == frozenset()


def test_create_minimal():
    settings = SchemaParserSettings.create(**MINIMAL_CONFIG)
    assert isinstance(settings, SchemaParserSettings)
    assert settings.index_key == "index"
    assert settings.model_name == "MyModel"
    assert settings.allowed_types == ()
    assert settings.type_aliases == frozenset()


def test_create_full():
    settings = SchemaParserSettings.create(**FULL_CONFIG)
    assert settings.allowed_types == ("int", "str")
    assert settings.type_aliases_dict == {
        "number": ["int", "float"],
        "text": ["str"],
    }


def test_from_dict():
    settings = SchemaParserSettings.from_dict(FULL_CONFIG)
    assert isinstance(settings, SchemaParserSettings)
    assert settings.allowed_types == ("int", "str")


def test_from_yaml():
    yaml_str = yaml.safe_dump(FULL_CONFIG)
    settings = SchemaParserSettings.from_yaml(yaml_str)
    assert isinstance(settings, SchemaParserSettings)
    assert settings.type_aliases_dict["number"] == ["int", "float"]


def test_from_json():
    json_str = json.dumps(FULL_CONFIG)
    settings = SchemaParserSettings.from_json(json_str)
    assert isinstance(settings, SchemaParserSettings)
    assert settings.allowed_types == ("int", "str")


def test_invalid_type_aliases():
    config = {**MINIMAL_CONFIG, "type_aliases": ["not", "a", "dict"]}
    with pytest.raises(TypeError):
        SchemaParserSettings.create(**config)


def test_invalid_allowed_types():
    config = {**MINIMAL_CONFIG, "allowed_types": "not-a-list"}
    settings = SchemaParserSettings.create(**config)
    # Pydantic converts string to tuple of characters
    assert settings.allowed_types == tuple("not-a-list")


@pytest.mark.parametrize(
    "legacy_key",
    ["schema_key", "type_key", "default_key", "constraints_key", "metadata_key"],
)
def test_legacy_custom_document_key_settings_raise(legacy_key):
    with pytest.raises(SettingsError):
        SchemaParserSettings.create(**{legacy_key: "custom"})
