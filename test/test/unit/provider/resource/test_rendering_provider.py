from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from templisafe.engine.template_engine import TemplateEngine
from templisafe.provider.resource.rendering_provider import RenderingProvider
from templisafe.template.renderer.renderer import Renderer, Rendering
from templisafe.template.template_model import (
    CompilationSpec,
    Outcome,
    Schema,
    Template,
    VariantSet,
)


@pytest.fixture
def provider() -> RenderingProvider:
    """Return a RenderingProvider instance."""
    return RenderingProvider()


class DummySchema(BaseModel):
    name: str


@pytest.fixture
def compiled() -> CompilationSpec:
    """Return a dummy compiled template."""
    template = Template(template_str="Hello {{ name }}!", vars={"name"})
    schema = Schema(model_cls=DummySchema)
    return CompilationSpec(template=template, schema=schema)


@pytest.fixture
def variant_set() -> VariantSet:
    """Return a dummy variant set."""
    from templisafe.template.template_model import Variant

    return VariantSet(variants=[Variant(name="v1")])


@pytest.fixture
def engine() -> TemplateEngine:
    """Return a mocked TemplateEngine."""
    engine_mock = Mock(spec=TemplateEngine)
    engine_mock.extract_variables.return_value = {"var"}
    return engine_mock


@pytest.fixture
def renderer() -> Renderer:
    """Return a mocked Renderer."""
    renderer_mock = Mock(spec=Renderer)
    renderer_mock.validate.return_value = Rendering(outcome=Outcome.SUCCESS, message="ok")
    renderer_mock.render.return_value = Rendering(outcome=Outcome.SUCCESS, message="ok")
    return renderer_mock


def test_provide_validation(provider, compiled, variant_set, renderer):
    """Validation is delegated to the Renderer."""
    result = provider.provide_validation(compiled, variant_set, renderer)
    assert isinstance(result, Rendering)
    renderer.validate.assert_called_once_with(compiled, variant_set)


def test_provide_rendering(provider, compiled, variant_set, engine, renderer):
    """Rendering is delegated to the Renderer with the TemplateEngine."""
    result = provider.provide_rendering(compiled, variant_set, engine, renderer)
    assert isinstance(result, Rendering)
    renderer.render.assert_called_once_with(compiled, variant_set, engine)
