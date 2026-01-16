from pydantic import BaseModel
import pytest
from unittest.mock import create_autospec, AsyncMock
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
from templisafe.loader.loader_facade import LoaderFacade
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

    # Template engine
    engine = create_autospec(TemplateEngine)
    engine_manager = create_autospec(TemplateEngineManager)
    engine_manager.get_or_create.return_value = engine

    # Loader facade
    loader = create_autospec(LoaderFacade)
    loader.load_template.return_value = template
    loader.load_schema.return_value = schema
    loader.load_variants = AsyncMock(return_value=variants)
    loader.load_settings.return_value = None

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
        source_manager=source_manager,
        template_engine_manager=engine_manager,
        loader_facade=loader,
        compiler_manager=compiler_manager,
        renderer_manager=renderer_manager,
        outcome_handler=outcome_handler,
        engine_default_settings=TemplateEngineSettings(kind=TemplateEngineKind.JINJA, config={}),
        compiler_default_settings=CompilerSettings(index_key="_index"),
        renderer_default_settings=RendererSettings(index_key="_index"),
    )


def test_compile_sync_calls_acompile_and_returns_compilation(templater):
    result = templater.compile(template_source=create_autospec(Source))
    assert isinstance(result, Compilation)


@pytest.mark.asyncio
async def test_acompile_calls_compiler_and_outcome_handler(templater):
    result = await templater.acompile(template_source=create_autospec(Source))

    assert isinstance(result, Compilation)
    templater._outcome_handler.handle_compilation.assert_called_once_with(result)


def test_render_sync_returns_rendering(templater):
    result = templater.render(
        compiled="COMPILED",
        variants_sources=create_autospec(Source)
    )
    assert isinstance(result, Rendering)


@pytest.mark.asyncio
async def test_arender_calls_renderer_and_outcome_handler(templater):
    result = await templater.arender(
        compiled="COMPILED",
        variants_sources=create_autospec(Source)
    )

    assert isinstance(result, Rendering)
    templater._outcome_handler.handle_rendering.assert_called_once_with(result)

def test_validate_sync_returns_rendering(templater):
    result = templater.validate(
        compiled="COMPILED",
        variants_sources=create_autospec(Source)
    )
    assert isinstance(result, Rendering)


@pytest.mark.asyncio
async def test_avalidate_calls_renderer_validate(templater):
    result = await templater.avalidate(
        compiled="COMPILED",
        variants_sources=create_autospec(Source)
    )

    assert isinstance(result, Rendering)
    templater._outcome_handler.handle_validation.assert_called_once_with(result)

def test_build_sync_returns_build(templater):
    result = templater.build(
        template_source=create_autospec(Source),
        variants_sources=create_autospec(Source),
    )

    assert isinstance(result, Build)
    assert isinstance(result.compilation, Compilation)
    assert isinstance(result.rendering, Rendering)


@pytest.mark.asyncio
async def test_abuild_runs_compile_then_render(templater):
    result = await templater.abuild(
        template_source=create_autospec(Source),
        variants_sources=create_autospec(Source),
    )

    assert isinstance(result, Build)
    assert isinstance(result.compilation, Compilation)
    assert isinstance(result.rendering, Rendering)



class SlowSource(Source):
    def __init__(self, delay: float):
        self.delay = delay

    def read(self) -> str:
        time.sleep(self.delay)
        return "data"
