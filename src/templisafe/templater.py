from typing import Any, Callable, Coroutine
from threading import Thread
import asyncio
from asyncio import Task, TaskGroup

from templisafe.outcome_handler import OutcomeHandler

from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.settings import Settings
from templisafe.settings.source_settings import SourceSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings

from templisafe.source.source_manager import SourceManager
from templisafe.source.source import Source

from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineManager

from templisafe.loader.loader_facade import LoaderFacade

from templisafe.template.template_model import (
    CompilationSpec, 
    Template, 
    Schema, 
    VariantSet,
    Compilation,
    Rendering,
    Build
)
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_manager import CompilerManager
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_manager import RendererManager


class Templater:
    """
    Central orchestrator for template workflows.

    Provides a high-level API to efficiently compile, render, validate and build templates
    with schemas, variants and template engines. Orchestrates source resolution, settings loading 
    and resource coordination concurrently, delegating tasks to the appropriate components.
    """

    __slots__: tuple[str, ...] = (
        "_source_manager", "_template_engine_manager", "_loader_facade", 
        "_compiler_manager", "_renderer_manager", "_outcome_handler",
        "_engine_default_settings", "_compiler_default_settings", "_renderer_default_settings"
    )
    
    def __init__(
        self,
        *,
        source_manager: SourceManager,
        template_engine_manager: TemplateEngineManager,
        loader_facade: LoaderFacade,
        compiler_manager: CompilerManager,
        renderer_manager: RendererManager,
        outcome_handler: OutcomeHandler,
        engine_default_settings: TemplateEngineSettings,
        compiler_default_settings: CompilerSettings,
        renderer_default_settings: RendererSettings
        
    ) -> None:
        self._source_manager: SourceManager = source_manager
        self._template_engine_manager: TemplateEngineManager = template_engine_manager
        self._loader_facade: LoaderFacade = loader_facade
        self._compiler_manager: CompilerManager = compiler_manager
        self._renderer_manager: RendererManager = renderer_manager
        self._outcome_handler: OutcomeHandler = outcome_handler

        self._engine_default_settings: TemplateEngineSettings = engine_default_settings
        self._compiler_default_settings: CompilerSettings = compiler_default_settings
        self._renderer_default_settings: RendererSettings = renderer_default_settings

    def _resolve_source(self, source_or_settings: Source | SourceSettings | None) -> Source | None:
        if isinstance(source_or_settings, SourceSettings):
            return self._source_manager.get_or_create(source_or_settings)
        return source_or_settings
    
    def _resolve_sources(
            self,
            sources: Source | SourceSettings | list[Source | SourceSettings],
            ) -> list[Source]:
        if not isinstance(sources, list):
            sources = [sources]
        
        resolved: list[Source] = []
        for s in sources:
            src: Source | None = self._resolve_source(s)
            if src is None:
                raise ValueError(f"Could not resolve source: {s!r}")
            resolved.append(src)

        return resolved
    
    async def _load_template_engine(self, template_engine_settings_source: Source | SourceSettings | None) -> TemplateEngine:
        template_engine_settings_actual_source: Source | None = self._resolve_source(template_engine_settings_source)
        
        template_engine_settings: Settings = (
            await asyncio.to_thread(
                self._loader_facade.load_settings, 
                template_engine_settings_actual_source
            )
            if template_engine_settings_actual_source is not None
            else self._engine_default_settings
        )
        if not isinstance(template_engine_settings, TemplateEngineSettings):
            raise ValueError(f"Wrong template engine settings provided: {template_engine_settings}")
        return self._template_engine_manager.get_or_create(template_engine_settings) 
    
    async def _load_template(
            self, 
            template_source: Source | SourceSettings,
            template_engine: TemplateEngine  | None,
            ) -> Template: 
        template_actual_source: Source | None = self._resolve_source(template_source)
        assert template_actual_source is not None
        
        return await asyncio.to_thread(
            self._loader_facade.load_template,
            template_actual_source,
            template_engine
        )
    
    async def _load_schema(
            self, 
            schema_source: Source | SourceSettings | None,
            schema_parser_settings_source: Source | SourceSettings | None,
            ) -> Schema | None: 
        schema_actual_source: Source | None = self._resolve_source(schema_source)
        if schema_actual_source is None:
            return None
        
        return await asyncio.to_thread(
            self._loader_facade.load_schema,
            schema_actual_source,
            self._resolve_source(schema_parser_settings_source)
        )
    
    async def _load_variants(
            self, 
            variants_sources: Source | SourceSettings | list[Source | SourceSettings],
            variant_parser_settings_source: Source | SourceSettings | None,
            ) -> VariantSet: 
        
        variants_actual_sources: list[Source] = self._resolve_sources(variants_sources)
        return await self._loader_facade.load_variants(
                variants_sources=variants_actual_sources,
                parser_settings_source=self._resolve_source(variant_parser_settings_source)
            )
    
    
    async def _load_compiler(self, compiler_settings_source: Source | SourceSettings | None) -> Compiler:
        compiler_settings_actual_source: Source | None = self._resolve_source(compiler_settings_source)
        compiler_settings: Settings = (
            await asyncio.to_thread(
                self._loader_facade.load_settings, 
                compiler_settings_actual_source
            ) 
            if compiler_settings_actual_source is not None
            else self._compiler_default_settings
        )
        if not isinstance(compiler_settings, CompilerSettings):
            raise ValueError(f"Wrong compiler settings provided: {compiler_settings}")
            
        return self._compiler_manager.get_or_create(compiler_settings)
    
    
    async def _load_renderer(self, renderer_settings_source: Source | SourceSettings | None) -> Renderer:
        renderer_settings_actual_source: Source | None = self._resolve_source(renderer_settings_source)
        renderer_settings: Settings = (
            await asyncio.to_thread(
                self._loader_facade.load_settings, 
                renderer_settings_actual_source
            ) 
            if renderer_settings_actual_source is not None
            else self._renderer_default_settings
        )
        if not isinstance(renderer_settings, RendererSettings):
            raise ValueError(f"Wrong renderer settings provided: {renderer_settings}")
            
        return self._renderer_manager.get_or_create(renderer_settings)

    def _arun(
        self, 
        coroutine: Callable[..., Coroutine], 
        **wargs: Any
    ) -> Any:
        """Run an async coroutine in a separate thread and block until it completes."""
        result_container: dict[str, Any] = {}

        def runner() -> None:
            result_container["result"] = asyncio.run(coroutine(**wargs))

        t: Thread = Thread(target=runner)
        t.start()
        t.join()

        return result_container["result"]

        
    async def acompile(
        self,
        template_source: Source | SourceSettings,
        schema_source: Source | SourceSettings | None = None,
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None,
        compiler_settings_source: Source | SourceSettings | None = None,
    ) -> Compilation:
        """
        Asynchronously compile a template with an optional schema.  

        Parameters
        ----------
        template_source : Source | SourceSettings
            Source of the template to compile.
        schema_source : Source | SourceSettings | None
            Optional source for schema used in compilation.
        template_engine_settings_source : Source | SourceSettings | None
            Optional source for template engine settings. If not provided, default configurations are used.
        schema_parser_settings_source : Source | SourceSettings | None
            Optional source for schema parser settings. If not provided, default configurations are used.
        compiler_settings_source : Source | SourceSettings | None
            Optional source for compiler settings. If not provided, default configurations are used.

        Returns
        -------
        Compilation
            The result of the compilation, including compilation spec and outcome.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution
            or compilation failures.
        """

        async with TaskGroup() as tg:
            engine_task: Task = tg.create_task(
                self._load_template_engine(template_engine_settings_source)
            )

            schema_task: Task = tg.create_task(
                self._load_schema(
                    schema_source,
                    schema_parser_settings_source,
                )
            )

            compiler_task: Task = tg.create_task(
                self._load_compiler(compiler_settings_source)
            )

            # Wait for engine before starting
            async def load_template_after_engine() -> Template:
                engine: TemplateEngine = await engine_task
                return await self._load_template(
                    template_source,
                    engine,
                )
            
            template_task: Task = tg.create_task(load_template_after_engine())

        # TaskGroup guarantees all completed or raised
        template: Template = template_task.result()
        schema: Schema | None = schema_task.result()
        compiler: Compiler = compiler_task.result()
        
        compilation: Compilation = compiler.compile(template=template, schema=schema)
        self._outcome_handler.handle_compilation(compilation)
        return compilation
    
    def compile(
        self,
        template_source: Source | SourceSettings,
        schema_source: Source | SourceSettings | None = None,
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None,
        compiler_settings_source: Source | SourceSettings | None = None,
    ) -> Compilation:
        """
        Synchronously compile a template. Wraps `acompile` in a blocking call.

        Returns
        -------
        Compilation
            The result of the compilation.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution
            or compilation failures.
        """
        
        return self._arun(
            self.acompile, 
            template_source=template_source,
            schema_source=schema_source,
            template_engine_settings_source=template_engine_settings_source,
            schema_parser_settings_source=schema_parser_settings_source,
            compiler_settings_source=compiler_settings_source        
        )


    # ----------------------------
    # Rendering
    # ----------------------------
    async def arender(
        self, 
        compiled: CompilationSpec,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        variant_parser_settings_source: Source | SourceSettings | None = None,
        renderer_settings_source: Source | SourceSettings | None = None,
    ) -> Rendering:
        """
        Asynchronously render a compiled template using variants and a template engine.

        Parameters
        ----------
        compiled : CompilationSpec
            The compiled template to render.
        variants_sources : Source | SourceSettings | list[Source | SourceSettings]
            Sources of variant data.
        template_engine_settings_source : Source | SourceSettings | None
            Optional source for template engine settings. If not provided, default configurations are used.
        variant_parser_settings_source : Source | SourceSettings | None
            Optional source for variant parser settings. If not provided, default configurations are used.
        renderer_settings_source : Source | SourceSettings | None
            Optional source for renderer settings. If not provided, default configurations are used.

        Returns
        -------
        Rendering
            The rendered result including outcome and message.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution
            or rendering failures.
        """

        async with TaskGroup() as tg:
            engine_task: Task = tg.create_task(
                self._load_template_engine(template_engine_settings_source)
            )

            variants_set_task: Task = tg.create_task(
                self._load_variants(
                variants_sources,
                variant_parser_settings_source
                )
            )
            
            renderer_task: Task = tg.create_task(
                self._load_renderer(renderer_settings_source)
            )

        engine: TemplateEngine = engine_task.result()
        variants_set: VariantSet = variants_set_task.result()
        renderer: Renderer = renderer_task.result()

        rendering: Rendering = renderer.render(
            compiled=compiled, 
            variants_set=variants_set, 
            engine=engine
            )
        self._outcome_handler.handle_rendering(rendering)
        return rendering
    
    def render(
        self, 
        compiled: CompilationSpec,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        variant_parser_settings_source: Source | SourceSettings | None = None,
        renderer_settings_source: Source | SourceSettings | None = None,
    ) -> Rendering:
        """
        Synchronously render a compiled template. Wraps `arender` in a blocking call.

        Returns
        -------
        Rendering
            The rendered result.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution
            or rendering failures.
        """

        return self._arun(
            self.arender,
            compiled=compiled,
            variants_sources=variants_sources,
            template_engine_settings_source=template_engine_settings_source,
            variant_parser_settings_source=variant_parser_settings_source,
            renderer_settings_source=renderer_settings_source
            )

    # ----------------------------
    # Validation
    # ----------------------------
    async def avalidate(
        self, 
        compiled: CompilationSpec,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        *,
        variant_parser_settings_source: Source | SourceSettings | None = None,
        renderer_settings_source: Source | SourceSettings | None = None,
    ) -> Rendering:
        """
        Asynchronously validate a compiled template against variants without effectively rendering it.

        Parameters
        ----------
        compiled : CompilationSpec
            The compiled template to render.
        variants_sources : Source | SourceSettings | list[Source | SourceSettings]
            Sources of variant data.
        variant_parser_settings_source : Source | SourceSettings | None
            Optional source for variant parser settings. If not provided, default configurations are used.
        renderer_settings_source : Source | SourceSettings | None
            Optional source for renderer settings. If not provided, default configurations are used.

        Returns
        -------
        Rendering
            Validation result with outcome.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution
            or rendering validation failures.
        """

        async with TaskGroup() as tg:
            variants_set_task: Task = tg.create_task(
                self._load_variants(
                variants_sources,
                variant_parser_settings_source
                )
            )
            
            renderer_task: Task = tg.create_task(
                self._load_renderer(renderer_settings_source)
            )

        variants_set: VariantSet = variants_set_task.result()
        renderer: Renderer = renderer_task.result()

        rendering: Rendering = renderer.validate(compiled=compiled, variants_set=variants_set)
        self._outcome_handler.handle_validation(rendering)
        return rendering

    def validate(
        self, 
        compiled: CompilationSpec,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        *,
        variant_parser_settings_source: Source | SourceSettings | None = None,
        renderer_settings_source: Source | SourceSettings | None = None,
    ) -> Rendering:
        """
        Synchronously validate a compiled template. Wraps `avalidate` in a blocking call.

        Returns
        -------
        Rendering
            Validation result.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution
            or rendering validation failures.
        """

        return self._arun(
            self.avalidate,
            compiled=compiled,
            variants_sources=variants_sources,
            variant_parser_settings_source=variant_parser_settings_source,
            renderer_settings_source=renderer_settings_source
            )

    # ----------------------------
    # Build
    # ----------------------------
    async def abuild(
        self, 
        template_source: Source | SourceSettings,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        schema_source: Source | SourceSettings | None = None,
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None,
        variant_parser_settings_source: Source | SourceSettings | None = None,
        compiler_settings_source: Source | SourceSettings | None = None,
        renderer_settings_source: Source | SourceSettings | None = None
    ) -> Build:
        """
        Asynchronously compile, validate and render a template.
        Combines compilation, validation and rendering into a single call.

        Parameters
        ----------
        template_source : Source | SourceSettings
            Source of the template to compile.
        schema_source : Source | SourceSettings | None
            Optional source for schema used in compilation.
        variants_sources : Source | SourceSettings | list[Source | SourceSettings]
            Sources of variant data.
        template_engine_settings_source : Source | SourceSettings | None
            Optional source for template engine settings. If not provided, default configurations are used.
        schema_parser_settings_source : Source | SourceSettings | None
            Optional source for schema parser settings. If not provided, default configurations are used.
        variant_parser_settings_source : Source | SourceSettings | None
            Optional source for variant parser settings. If not provided, default configurations are used.
        compiler_settings_source : Source | SourceSettings | None
            Optional source for compiler settings. If not provided, default configurations are used.
        renderer_settings_source : Source | SourceSettings | None
            Optional source for renderer settings. If not provided, default configurations are used.

        Returns
        -------
        Build
            Contains `compilation` and `rendering` results.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution,
            compilation or rendering failures.
        """

        compilation: Compilation = await self.acompile(
            template_source=template_source,
            schema_source=schema_source,
            template_engine_settings_source=template_engine_settings_source,
            schema_parser_settings_source=schema_parser_settings_source,
            compiler_settings_source=compiler_settings_source,
        )

        rendering: Rendering = await self.arender(
            compiled=compilation.compiled,
            variants_sources=variants_sources,
            template_engine_settings_source=template_engine_settings_source,
            variant_parser_settings_source=variant_parser_settings_source,
            renderer_settings_source=renderer_settings_source
        )

        return Build(compilation=compilation, rendering=rendering)
    
    def build(
        self, 
        template_source: Source | SourceSettings,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        schema_source: Source | SourceSettings | None = None,
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None,
        variant_parser_settings_source: Source | SourceSettings | None = None,
        compiler_settings_source: Source | SourceSettings | None = None,
        renderer_settings_source: Source | SourceSettings | None = None,
    ) -> Build:
        """
        Synchronously build a template. Wraps `abuild` in a blocking call.

        Returns
        -------
        Build
            Contains compilation and rendering results.

        Raises
        ------
        Exception
            May raise exceptions related to invalid settings, source resolution,
            compilation or rendering failures.
        """

        return self._arun(
            self.abuild,
            template_source=template_source,
            variants_sources=variants_sources,
            schema_source=schema_source,
            template_engine_settings_source=template_engine_settings_source,
            schema_parser_settings_source=schema_parser_settings_source,
            variant_parser_settings_source=variant_parser_settings_source,
            compiler_settings_source=compiler_settings_source,
            renderer_settings_source=renderer_settings_source
        )

