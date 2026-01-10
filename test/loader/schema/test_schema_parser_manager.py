import pytest
from templisafe.loader.schema.schema_parser_manager import SchemaParserFactory, SchemaParserManager
from templisafe.loader.schema.yaml_schema_parser import YamlSchemaParser
from templisafe.settings.parser.schema_parser_settings import SchemaParserSettings, YamlSchemaParserSettings
from templisafe.util.util import ContentType
from templisafe.exceptions.schema_error import UnsupportedSchemaParserError

'''
# -----------------------
# Factory tests
# -----------------------
def test_factory_create_known():
    settings = YamlQSchemaParserSettings(
        schema_key="schema",
        type_key="type",
        default_key="default",
        allowed_types=("int",)
    )
    factory = QSchemaParserFactory()
    parser = factory.create(settings)
    assert isinstance(parser, QYamlSchemaParser)
    assert parser._settings == settings

def test_factory_create_unknown():
    class DummySettings(QSchemaParserSettings):
        @property
        def content_type(self):
            return ContentType.YAML

    settings = DummySettings(
        schema_key="schema",
        type_key="type",
        default_key="default",
        allowed_types=("int",)
    )
    factory = QSchemaParserFactory()
    with pytest.raises(UnimplementedSchemaParserError):
        factory.create(settings)

# -----------------------
# Manager tests
# -----------------------
def test_manager_get_or_create_and_contains():
    manager = QSchemaParserManager()

    # Create parser with default settings
    default_settings = YamlQSchemaParserSettings(
        schema_key="schema",
        type_key="type",
        default_key="default",
        allowed_types=("str", "float")
    )
    parser1 = manager.get_or_create(default_settings)
    assert isinstance(parser1, QYamlSchemaParser)
    assert parser1._settings == default_settings
    assert default_settings in manager

    # Create parser with custom settings
    custom_settings = YamlQSchemaParserSettings(
        schema_key="custom_schema",
        type_key="custom_type",
        default_key="custom_default",
        allowed_types=("int",)
    )
    parser2 = manager.get_or_create(custom_settings)
    assert isinstance(parser2, QYamlSchemaParser)
    assert parser2._settings == custom_settings
    assert custom_settings in manager

    # Ensure the same instance is returned on repeated get_or_create
    parser1_again = manager.get_or_create(default_settings)
    assert parser1 is parser1_again
'''