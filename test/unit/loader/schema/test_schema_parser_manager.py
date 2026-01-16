import pytest
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.loader.schema.schema_parser import SchemaParser
from templisafe.loader.schema.schema_parser_manager import SchemaParserFactory, SchemaParserManager


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
        type_aliases={"int": ["integer"], "str": ["string"], "float": ["real", "number"]},  # type: ignore
    )


def test_factory_creates_parser(settings):
    factory = SchemaParserFactory()
    parser = factory.create(settings)
    assert isinstance(parser, SchemaParser)
    # Ensure the parser retains the settings
    assert parser._settings == settings


def test_manager_creates_and_caches_parser(settings):
    manager = SchemaParserManager()
    
    # Initially, manager has no parsers
    assert settings not in manager
    
    # Create a parser
    parser1 = manager.get_or_create(settings)
    assert isinstance(parser1, SchemaParser)
    
    # Now settings should be in manager
    assert settings in manager
    
    # Re-fetch the parser should return the same instance
    parser2 = manager.get_or_create(settings)
    assert parser1 is parser2  # caching works


def test_manager_with_initial_parsers(settings):
    pre_created_parser = SchemaParser(settings)
    manager = SchemaParserManager(parsers={settings: pre_created_parser})
    
    # The parser should be the same as pre-created
    parser = manager.get_or_create(settings)
    assert parser is pre_created_parser
    assert settings in manager


def test_manager_creates_multiple_parsers():
    # Create multiple distinct settings
    settings1 = SchemaParserSettings(
        schema_key="parameters1",
        type_key="type",
        default_key="default",
        constraints_key="constraints",
        metadata_key="metadata",
        index_key="_index",
        model_name="Model1",
        allowed_types=("int", "str"),
        type_aliases={},                # type: ignore
    )
    settings2 = SchemaParserSettings(
        schema_key="parameters2",
        type_key="type",
        default_key="default",
        constraints_key="constraints",
        metadata_key="metadata",
        index_key="_index",
        model_name="Model2",
        allowed_types=("int", "str"),
        type_aliases={},                # type: ignore
    )

    manager = SchemaParserManager()
    parser1 = manager.get_or_create(settings1)
    parser2 = manager.get_or_create(settings2)

    assert parser1 is not parser2
    assert settings1 in manager
    assert settings2 in manager
