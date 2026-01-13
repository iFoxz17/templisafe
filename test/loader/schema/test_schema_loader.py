import pytest
from pydantic import BaseModel
from typing import Any, Dict

from templisafe.loader.schema.schema_loader import SchemaLoader, SCHEMA_PARSER_SETTINGS_YAML
from templisafe.loader.schema.schema_parser_manager import SchemaParserManager
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.loader.schema.schema_parser import SchemaParser
from templisafe.template.template_model import Schema
from templisafe.exceptions.schema_error import IllegalSchemaDefinitionError, UnsupportedSchemaParserError


@pytest.fixture
def loader() -> SchemaLoader:
    return SchemaLoader()


@pytest.fixture
def settings() -> SchemaParserSettings:
    return SchemaParserSettings.from_yaml(SCHEMA_PARSER_SETTINGS_YAML)


def _getattr(instance: BaseModel, name: str):
    return getattr(instance, name)


def test_default_settings(loader: SchemaLoader):
    # The loader should have default settings loaded from YAML
    assert loader._default_settings is not None
    assert isinstance(loader._default_settings, SchemaParserSettings)
    assert loader._manager is not None
    assert isinstance(loader._manager, SchemaParserManager)


def test_resolve_settings(loader: SchemaLoader, settings: SchemaParserSettings):
    # If we provide settings, they should be returned
    resolved = loader._resolve_settings(settings)
    assert resolved is settings

    # If no settings provided, default settings are returned
    resolved_default = loader._resolve_settings(None)
    assert resolved_default is loader._default_settings


def test_load_simple_schema(loader: SchemaLoader):
    schema_config: Dict[str, Any] = {
        "schema": {
            "age": {"type": "int", "default": 30},
            "name": "str"
        }
    }

    schema: Schema = loader.load(schema_config)
    model_cls = schema.model_cls
    assert issubclass(model_cls, BaseModel)

    instance = model_cls(name="Alice")
    assert _getattr(instance, "age") == 30
    assert _getattr(instance, "name") == "Alice"

    # Ensure metadata index is correctly added
    model_fields = getattr(model_cls, "model_fields")
    age = model_fields['age']
    age_metadata = getattr(age, "json_schema_extra")
    assert age_metadata["_index"] == 0
    name = model_fields['name']
    name_metadata = getattr(name, "json_schema_extra")
    assert name_metadata["_index"] == 1


def test_load_custom_settings(loader: SchemaLoader):
    default_settings = SchemaParserSettings.from_yaml(SCHEMA_PARSER_SETTINGS_YAML)
    custom_settings = default_settings.model_copy(update={"model_name": "CustomModel"})

    schema_config: Dict[str, Any] = {
        "schema": {
            "flag": {"type": "bool", "default": True}
        }
    }

    schema: Schema = loader.load(schema_config, parser_settings=custom_settings)
    model_cls = schema.model_cls
    instance = model_cls()
    assert _getattr(instance, "flag") is True
    assert model_cls.__name__ == "CustomModel"


def test_parser_manager_caching(loader: SchemaLoader):
    # Load the same schema twice with default settings
    schema_config: Dict[str, Any] = {
        "schema": {"field1": "str"}
    }

    parser1: SchemaParser = loader._manager.get_or_create(loader._default_settings)
    schema1 = loader.load(schema_config)

    parser2: SchemaParser = loader._manager.get_or_create(loader._default_settings)
    schema2 = loader.load(schema_config)

    # The parser instance should be cached and identical
    assert parser1 is parser2
    assert isinstance(schema1, Schema)
    assert isinstance(schema2, Schema)
