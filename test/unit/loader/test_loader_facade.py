import pytest
from unittest.mock import create_autospec

from pydantic import BaseModel

from templisafe.loader.loader_facade import LoaderFacade
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader
from templisafe.template.template_model import Template, Schema, VariantSet
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.engine.template_engine import TemplateEngine


# -------------------------
# Fixtures for loaders
# -------------------------
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
def facade(template_loader, schema_loader, variant_loader) -> LoaderFacade:
    return LoaderFacade(
        template_loader=template_loader,
        schema_loader=schema_loader,
        variant_loader=variant_loader
    )

class DummySchemaParserSettings(SchemaParserSettings):
    # Ignore extra fields and fill required fields with dummy values
    model_config = {"extra": "ignore"}

    def __init__(self, **data):
        defaults = {
            "schema_key": "dummy_schema",
            "type_key": "dummy_type",
            "default_key": "dummy_default",
            "constraints_key": "dummy_constraints",
            "metadata_key": "dummy_metadata",
            "index_key": "dummy_index",
            "model_name": "DummyModel",
            "allowed_types": (),
            "type_aliases": {},
        }
        defaults.update(data)
        super().__init__(**defaults)            # type: ignore

class DummyVariantParserSettings(VariantParserSettings):
    model_config = {"extra": "ignore"}

    def __init__(self, **data):
        defaults = {
            "variants_key": "dummy_variants",
            "default_variants_name": "default_dummy",
            "variant_name_key": "dummy_name",
            "bindings_key": "dummy_bindings",
        }
        defaults.update(data)
        super().__init__(**defaults)

@pytest.fixture
def dummy_schema_parser_settings() -> SchemaParserSettings:
    return DummySchemaParserSettings()

@pytest.fixture
def dummy_variant_parser_settings() -> VariantParserSettings:
    return DummyVariantParserSettings()


# -------------------------
# Tests
# -------------------------
def test_load_template_calls_template_loader(facade, template_loader):
    template_str = "{{ x }}"
    mock_template = Template(template_str=template_str, vars={"x"})
    template_loader.load.return_value = mock_template

    result = facade.load_template(template_str)

    template_loader.load.assert_called_once_with(template_str, None)
    assert result == mock_template


def test_load_template_with_engine(facade, template_loader):
    template_str = "{{ x }}"
    mock_engine = create_autospec(TemplateEngine)
    mock_template = Template(template_str=template_str, vars={"x"})
    template_loader.load.return_value = mock_template

    result = facade.load_template(template_str, engine=mock_engine)

    template_loader.load.assert_called_once_with(template_str, mock_engine)
    assert result == mock_template


def test_load_schema_calls_schema_loader(facade, schema_loader, dummy_schema_parser_settings):
    schema_config = {"parameters": {}}
    mock_schema = Schema(model_cls=BaseModel)
    schema_loader.load.return_value = mock_schema

    result = facade.load_schema(schema_config, parser_settings=dummy_schema_parser_settings)

    schema_loader.load.assert_called_once_with(schema_config, dummy_schema_parser_settings)
    assert result == mock_schema


def test_load_variants_calls_variant_loader(facade, variant_loader, dummy_variant_parser_settings):
    variants_configs = [{"vars": {"x": 1}}, {"vars": {"y": 2}}]
    mock_variant_set = VariantSet([])
    variant_loader.load.return_value = mock_variant_set

    result = facade.load_variants(variants_configs, parser_settings=dummy_variant_parser_settings)

    variant_loader.load.assert_called_once_with(variants_configs, dummy_variant_parser_settings)
    assert result == mock_variant_set


# -------------------------
# Test load_variants with empty list
# -------------------------
def test_load_variants_empty_list(facade, variant_loader):
    variants_configs = []
    mock_variant_set = VariantSet([])
    variant_loader.load.return_value = mock_variant_set

    result = facade.load_variants(variants_configs)

    variant_loader.load.assert_called_once_with(variants_configs, None)
    assert result == mock_variant_set
