import pytest
import json
import yaml

from templisafe.settings.parser.schema_parser_settings import (
    SchemaParserSettings,
    YamlSchemaParserSettings,
)
from templisafe.util.util import ContentType


# ---------------------------------------------------------------------------
# Minimal concrete class for testing SchemaParserSettings
# ---------------------------------------------------------------------------
class DummySchemaSettings(SchemaParserSettings):
    @property
    def kind(self) -> ContentType:
        return ContentType.YAML


# ---------------------------------------------------------------------------
# Sample configuration data
# ---------------------------------------------------------------------------
MINIMAL_CONFIG = {
    "schema_key": "schema",
    "type_key": "type",
    "default_key": "default",
    "constraints_key": "constraints",
    "metadata_key": "metadata",
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
def test_create_minimal():
    settings = DummySchemaSettings.create(**MINIMAL_CONFIG)
    assert isinstance(settings, DummySchemaSettings)
    assert settings.schema_key == "schema"
    assert settings.allowed_types == ()
    assert settings.type_aliases == frozenset()


def test_create_full():
    settings = DummySchemaSettings.create(**FULL_CONFIG)
    assert settings.allowed_types == ("int", "str")
    assert settings.type_aliases_dict == {
        "number": ["int", "float"],
        "text": ["str"],
    }


def test_from_dict():
    settings = DummySchemaSettings.from_dict(FULL_CONFIG)
    assert isinstance(settings, DummySchemaSettings)
    assert settings.allowed_types == ("int", "str")


def test_from_yaml():
    yaml_str = yaml.safe_dump(FULL_CONFIG)
    settings = DummySchemaSettings.from_yaml(yaml_str)
    assert isinstance(settings, DummySchemaSettings)
    assert settings.type_aliases_dict["number"] == ["int", "float"]


def test_from_json():
    json_str = json.dumps(FULL_CONFIG)
    settings = DummySchemaSettings.from_json(json_str)
    assert isinstance(settings, DummySchemaSettings)
    assert settings.allowed_types == ("int", "str")


def test_invalid_type_aliases():
    config = {**MINIMAL_CONFIG, "type_aliases": ["not", "a", "dict"]}
    with pytest.raises(TypeError):
        DummySchemaSettings.create(**config)


def test_invalid_allowed_types():
    config = {**MINIMAL_CONFIG, "allowed_types": "not-a-list"}
    settings = DummySchemaSettings.create(**config)
    # Pydantic converts string to tuple of characters
    assert settings.allowed_types == tuple("not-a-list")


def test_yaml_schema_parser_settings_kind():
    yaml_settings = YamlSchemaParserSettings.create(**MINIMAL_CONFIG)
    assert yaml_settings.kind == ContentType.YAML


def test_missing_required_field():
    incomplete = MINIMAL_CONFIG.copy()
    incomplete.pop("schema_key")
    with pytest.raises(ValueError):
        DummySchemaSettings.create(**incomplete)


def test_dispatch_with_kind():
    # Using the registry dispatch for ContentType
    FULL_CONFIG_WITH_KIND = {**MINIMAL_CONFIG, "kind": "yaml"}
    settings = SchemaParserSettings.create(**FULL_CONFIG_WITH_KIND)
    assert isinstance(settings, YamlSchemaParserSettings)
    assert settings.kind == ContentType.YAML
