from pydantic import BaseModel
import pytest
from unittest.mock import Mock

from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.provider.resource.config_provider import ConfigProvider
from templisafe.provider.resource.settings_provider import SettingsProvider
from templisafe.provider.resource.template_provider import TemplateProvider
from templisafe.provider.resource.schema_provider import SchemaProvider
from templisafe.provider.resource.variant_provider import VariantProvider
from templisafe.provider.resource.compilation_provider import CompilationProvider
from templisafe.provider.resource.rendering_provider import RenderingProvider

from templisafe.parser.config.config_parser import ConfigParser, Config
from templisafe.parser.settings.settings_parser import SettingsParser, Settings
from templisafe.parser.template.template_parser import TemplateParser, Template
from templisafe.parser.schema.schema_parser import SchemaParser, Schema
from templisafe.parser.variant.variant_parser import VariantParser, VariantSet
from templisafe.template.compiler.compiler import Compiler, Compilation
from templisafe.template.renderer.renderer import Renderer, Rendering
from templisafe.template.template_model import Binding, CompilationSpec, Outcome, Variant
from templisafe.engine.template_engine import TemplateEngine


@pytest.fixture
def mock_providers():
    """Return a dict of mocked providers for testing."""
    return {
        "config": Mock(spec=ConfigProvider),
        "settings": Mock(spec=SettingsProvider),
        "template": Mock(spec=TemplateProvider),
        "schema": Mock(spec=SchemaProvider),
        "variant": Mock(spec=VariantProvider),
        "compilation": Mock(spec=CompilationProvider),
        "rendering": Mock(spec=RenderingProvider),
    }


@pytest.fixture
def resource_provider(mock_providers):
    """ResourceProvider initialized with mocked providers."""
    return ResourceProvider(
        config_provider=mock_providers["config"],
        settings_provider=mock_providers["settings"],
        template_provider=mock_providers["template"],
        schema_provider=mock_providers["schema"],
        variant_provider=mock_providers["variant"],
        compilation_provider=mock_providers["compilation"],
        rendering_provider=mock_providers["rendering"],
    )


# -----------------------------
# Tests
# -----------------------------

def test_provide_config(resource_provider, mock_providers):
    parser = Mock(spec=ConfigParser)
    payload = "dummy payload"
    expected = {"test": 1}
    mock_providers["config"].provide.return_value = expected

    result = resource_provider.provide_config(payload, parser)

    mock_providers["config"].provide.assert_called_once_with(payload, parser)
    assert result is expected


def test_provide_settings(resource_provider, mock_providers):
    config = {"kind": "compiler_settings", "index_key": "index"}
    parser = Mock(spec=SettingsParser)
    expected = Settings()
    mock_providers["settings"].provide.return_value = expected

    result = resource_provider.provide_settings(config, parser)

    mock_providers["settings"].provide.assert_called_once_with(config, parser)
    assert result is expected


def test_provide_template(resource_provider, mock_providers):
    template_str = "hello {{ var }}"
    engine = Mock(spec=TemplateEngine)
    parser = Mock(spec=TemplateParser)
    expected = Template(template_str=template_str, vars={"var"})
    mock_providers["template"].provide.return_value = expected

    result = resource_provider.provide_template(template_str, engine, parser)

    mock_providers["template"].provide.assert_called_once_with(template_str, engine, parser)
    assert result is expected

class DummySchema(BaseModel):
    var: str

def test_provide_schema(resource_provider, mock_providers):
    config = {"schema": {"var": "string"}}
    parser = Mock(spec=SchemaParser)
    expected = Schema(model_cls=DummySchema)
    mock_providers["schema"].provide.return_value = expected

    result = resource_provider.provide_schema(config, parser)

    mock_providers["schema"].provide.assert_called_once_with(config, parser)
    assert result is expected


def test_provide_variant(resource_provider, mock_providers):
    config = {"variants": {"variant1": {"var": "var1"}}}
    parser = Mock(spec=VariantParser)
    expected = VariantSet([Variant("variant1", [Binding(0, "var", "var1")])])
    mock_providers["variant"].provide.return_value = expected

    result = resource_provider.provide_variant(config, parser)

    mock_providers["variant"].provide.assert_called_once_with(config, parser)
    assert result is expected


def test_provide_compilation(resource_provider, mock_providers):
    template = Template("Hello {{var}}", {"var"})
    schema = Schema(DummySchema)
    compiler = Mock(spec=Compiler)
    expected = Compilation(outcome=Outcome.SUCCESS, message="ok")
    mock_providers["compilation"].provide.return_value = expected

    result = resource_provider.provide_compilation(template, schema, compiler)

    mock_providers["compilation"].provide.assert_called_once_with(template, schema, compiler)
    assert result is expected


def test_provide_rendering_and_validation(resource_provider, mock_providers):
    compiled = Mock(spec=CompilationSpec)
    variant_set = Mock(spec=VariantSet)
    engine = Mock(spec=TemplateEngine)
    renderer = Mock(spec=Renderer)
    expected_rendering = Mock(spec=Rendering)
    mock_providers["rendering"].provide_rendering.return_value = expected_rendering
    mock_providers["rendering"].provide_validation.return_value = expected_rendering

    result_render = resource_provider.provide_rendering(compiled, variant_set, engine, renderer)
    result_validation = resource_provider.provide_validation(compiled, variant_set, renderer)

    mock_providers["rendering"].provide_rendering.assert_called_once_with(compiled, variant_set, engine, renderer)
    mock_providers["rendering"].provide_validation.assert_called_once_with(compiled, variant_set, renderer)
    assert result_render is expected_rendering
    assert result_validation is expected_rendering
