from ast import Load
from pydantic import BaseModel
import pytest
from unittest.mock import create_autospec

from templisafe.settings.settings import Settings
from templisafe.loader.loader_facade import LoaderFacade
from templisafe.loader.config.config_loader import ConfigLoader
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader
from templisafe.source.source import Source
from templisafe.template.template_model import Template, Schema, VariantSet

# -------------------------
# Dummy Settings subclass
# -------------------------
class DummySettings(Settings):
    foo: str
    bar: int

    @classmethod
    def _parse_config(cls, config: dict, **kwargs) -> "DummySettings":
        return cls.model_validate(config)

# -------------------------
# Fixtures for the loaders
# -------------------------
@pytest.fixture
def config_loader():
    return create_autospec(ConfigLoader)

@pytest.fixture
def template_loader():
    return create_autospec(TemplateLoader)

@pytest.fixture
def schema_loader():
    return create_autospec(SchemaLoader)

@pytest.fixture
def variant_loader():
    return create_autospec(VariantLoader)

@pytest.fixture
def facade(config_loader, template_loader, schema_loader, variant_loader) -> LoaderFacade:
    return LoaderFacade(
        config_loader=config_loader,
        template_loader=template_loader,
        schema_loader=schema_loader,
        variant_loader=variant_loader
    )

@pytest.fixture
def source():
    return create_autospec(Source)

# -------------------------
# Tests
# -------------------------
def test_load_settings_calls_config_loader(facade: LoaderFacade, config_loader, source):
    # Prepare dummy Settings
    mock_settings = DummySettings.model_validate({"foo": "bar", "bar": 42})
    config_loader.load_settings.return_value = mock_settings

    result = facade.load_settings(source)
    
    config_loader.load_settings.assert_called_once_with(source)
    assert result == mock_settings

def test_load_template_calls_template_loader(facade: LoaderFacade, template_loader, source):
    mock_template = Template(template_str="{{ x }}", vars={"x"})
    template_loader.load.return_value = mock_template

    result = facade.load_template(source)

    template_loader.load.assert_called_once_with(source, None)
    assert result == mock_template

def test_load_schema_calls_schema_loader_and_config_loader(facade: LoaderFacade, schema_loader, config_loader, source):
    mock_schema = Schema(model_cls=BaseModel)
    schema_loader.load.return_value = mock_schema
    config_loader.load_config.return_value = {"parameters": {}}

    result = facade.load_schema(source)

    config_loader.load_config.assert_called_once_with(source)
    schema_loader.load.assert_called_once_with({"parameters": {}}, None)
    assert result == mock_schema

def test_load_variants_calls_variant_loader_and_config_loader(facade: LoaderFacade, variant_loader, config_loader):
    mock_variant_set = VariantSet([])
    variant_loader.load.return_value = mock_variant_set

    source1 = create_autospec(Source)
    source2 = create_autospec(Source)
    config_loader.load_config.side_effect = [{"vars": {}}, {"vars": {}}]

    result = facade.load_variants([source1, source2])

    assert config_loader.load_config.call_count == 2
    variant_loader.load.assert_called_once_with([{"vars": {}}, {"vars": {}}], None)
    assert result == mock_variant_set

def test_load_schema_with_wrong_settings_type_raises(facade: LoaderFacade, config_loader, source):
    # Provide a parser settings that is NOT SchemaParserSettings
    config_loader.load_settings.return_value = DummySettings.model_validate({"foo": "bar", "bar": 42})
    config_loader.load_config.return_value = {"parameters": {}}

    with pytest.raises(ValueError):
        facade.load_schema(source, parser_settings_source=source)

def test_load_variants_with_wrong_settings_type_raises(facade: LoaderFacade, config_loader):
    # Provide a parser settings that is NOT VariantParserSettings
    config_loader.load_settings.return_value = DummySettings.model_validate({"foo": "bar", "bar": 42})
    source1 = create_autospec(Source)
    source2 = create_autospec(Source)
    config_loader.load_config.side_effect = [{"vars": {}}, {"vars": {}}]

    with pytest.raises(ValueError):
        facade.load_variants([source1, source2], parser_settings_source=source1)
