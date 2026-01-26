from pydantic import BaseModel
import pytest
from unittest.mock import create_autospec
import time

from templisafe.settings.template_engine_settings import TemplateEngineKind, TemplateEngineSettings
from templisafe.templater import Templater
from templisafe.outcome_handler import OutcomeHandler
from templisafe.template.template_model import (
    CompilationSpec, Parameterization, RenderingSpec, Template, Schema, VariantSet,
    Compilation, Rendering, Build, Outcome
)
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.source.source import Source
from templisafe.source.source_manager import SourceManager
from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineManager
from templisafe.parser.loader_facade import LoaderFacade
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_manager import CompilerManager
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_manager import RendererManager
from templisafe.source.source import Source


@pytest.fixture
def template():
    return Template(template_str="hello {{ x }}", vars={"x"})


@pytest.fixture
def schema():
    return Schema(model_cls=BaseModel)


@pytest.fixture
def variants():
    return VariantSet([])


@pytest.fixture
def compilation(template, schema):
    return Compilation(
        message="Compilation successful",
        _spec=CompilationSpec(
            template=template,
            schema=schema
        ),
        outcome=Outcome.SUCCESS,
    )


@pytest.fixture
def rendering():
    return Rendering(
        message="Rendering successful",
        _spec=RenderingSpec(
            params=[]
        ),
        outcome=Outcome.SUCCESS,
    )


@pytest.fixture
def templater(
    template,
    schema,
    variants,
    compilation,
    rendering,
):
    # Sources
    source = create_autospec(Source)

    # Source manager
    source_manager = create_autospec(SourceManager)
    source_manager.get_or_create.return_value = source

    # Source resolver
    result: SourceResolutionResult = create_autospec(SourceResolutionResult)
    source_resolver = create_autospec(SourceResolver)
    source_resolver.resolve.return_value = result

    # Template engine
    engine = create_autospec(TemplateEngine)
    engine_manager = create_autospec(TemplateEngineManager)
    engine_manager.get_or_create.return_value = engine

    # Loader facade
    loader = create_autospec(LoaderFacade)
    loader.load_template.return_value = template
    loader.load_schema.return_value = schema
    loader.load_variants.return_value = variants

    # Compiler
    compiler = create_autospec(Compiler)
    compiler.compile.return_value = compilation
    compiler_manager = create_autospec(CompilerManager)
    compiler_manager.get_or_create.return_value = compiler

    # Renderer
    renderer = create_autospec(Renderer)
    renderer.render.return_value = rendering
    renderer.validate.return_value = rendering
    renderer_manager = create_autospec(RendererManager)
    renderer_manager.get_or_create.return_value = renderer

    # Outcome handler
    outcome_handler = create_autospec(OutcomeHandler)

    return Templater(
        source_executor=source_manager,
        source_resolver=source_resolver,
        template_engine_resolver=engine_manager,
        loader_facade=loader,
        compiler_manager=compiler_manager,
        renderer_manager=renderer_manager,
        outcome_handler=outcome_handler,
        template_engine_default_settings=TemplateEngineSettings(engine_kind=TemplateEngineKind.JINJA, config={}),
        compiler_default_settings=CompilerSettings(index_key="_index"),
        renderer_default_settings=RendererSettings(index_key="_index"),
    )


def test_compile_sync_calls_acompile_and_returns_compilation(templater):
    result = templater.compile(template=create_autospec(Source))
    assert isinstance(result, Compilation)


def test_render_sync_returns_rendering(templater):
    result = templater.render(
        compiled="COMPILED",
        variants=create_autospec(Source)
    )
    assert isinstance(result, Rendering)

def test_validate_sync_returns_rendering(templater):
    result = templater.validate(
        compiled="COMPILED",
        variants=create_autospec(Source)
    )
    assert isinstance(result, Rendering)


def test_build_sync_returns_build(templater):
    result = templater.build(
        template=create_autospec(Source),
        variants=create_autospec(Source),
    )

    assert isinstance(result, Build)
    assert isinstance(result.compilation, Compilation)
    assert isinstance(result.rendering, Rendering)