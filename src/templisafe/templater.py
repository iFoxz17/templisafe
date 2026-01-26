from templisafe.default_handler import DefaultHandler
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.outcome_handler import OutcomeHandler

from templisafe.executor.source_executor import SourceExecutorRequest, SourceExecutorResult, SourceExecutor
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings

from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.source.source import Source

from templisafe.engine.template_engine import TemplateEngine

from templisafe.parser.loader_facade import LoaderFacade

from templisafe.source.source_resolver import SourceResolver
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
    and resource coordination delegating tasks to the appropriate components.
    """

    __slots__: tuple[str, ...] = (
        "_source_resolver", "_template_engine_resolver", "_loader_facade",
        "_source_executor", 
        "_compiler_manager", "_renderer_manager",
        "_outcome_handler", "_default_handler"
    )
    
    def __init__(
        self,
        *,
        source_resolver: SourceResolver,
        template_engine_resolver: TemplateEngineResolver,
        source_executor: SourceExecutor,
        loader_facade: LoaderFacade,
        compiler_manager: CompilerManager,
        renderer_manager: RendererManager,
        default_handler: DefaultHandler,
        outcome_handler: OutcomeHandler,
        
    ) -> None:
        self._source_resolver: SourceResolver = source_resolver
        self._template_engine_resolver: TemplateEngineResolver = template_engine_resolver
        self._source_executor: SourceExecutor = source_executor
        self._loader_facade: LoaderFacade = loader_facade
        self._compiler_manager: CompilerManager = compiler_manager
        self._renderer_manager: RendererManager = renderer_manager
        self._default_handler: DefaultHandler = default_handler
        self._outcome_handler: OutcomeHandler = outcome_handler

    def _resolve_source(self, source: Source | SourceSettings | None) -> Source | None:
        return (
            self._source_resolver.resolve(source)
            if source is not None
            else None
        )
        
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
    
    def _resolve_template_engine(
            self, 
            template_engine: TemplateEngine | TemplateEngineSettings | None,
            ) -> TemplateEngine:
        if not isinstance(template_engine, TemplateEngine):
            template_engine = self._default_handler.template_engine_settings_or_default(
                template_engine
                )
        return self._template_engine_resolver.resolve(template_engine)
            
    # ----------------------------
    # Compilation
    # ----------------------------
    
    def _do_compile(
            self, 
            result: SourceExecutorResult, 
            template_engine: TemplateEngine      
        ) -> Compilation:
        
        if result.template_str is None:
            raise ValueError(f"Missing required template_str resolution: {result}")
        
        loader_facade: LoaderFacade = self._loader_facade
        template: Template = loader_facade.load_template(
            template_str=result.template_str,
            template_engine=template_engine,
            parser_settings=result.template_parser_settings
            )
        
        schema: Schema | None = None
        if result.schema_config is not None:
            schema = loader_facade.load_schema(
                schema_config=result.schema_config,
                parser_settings=result.schema_parser_settings
                )
        
        compiler_settings: CompilerSettings = (
            self
            ._default_handler
            .compiler_settings_or_default(
                result.compiler_settings
                )
        )
        compiler: Compiler = self._compiler_manager.get_or_create(compiler_settings) 
        
        compilation: Compilation = compiler.compile(template=template, schema=schema)
        self._outcome_handler.handle_compilation(compilation)
        return compilation
        
    def _compile(
        self,
        template: Source,
        schema: Source | None,
        template_engine: TemplateEngine,
        template_parser_settings: TemplateParserSettings | None = None,
        schema_parser_settings: SchemaParserSettings | None = None,
        compiler_settings: CompilerSettings | None = None,
    ) -> Compilation:
        return None

    def compile(
        self,
        template: Source | SourceSettings,
        schema: Source | SourceSettings | None = None,
        *,
        template_engine: Source | SourceSettings | TemplateEngineSettings | TemplateEngine | None = None,
        source_executor_settings: Source | SourceSettings | SourceExecutorSettings | None = None,
        template_parser_settings: Source | SourceSettings | TemplateParserSettings | None = None,
        schema_parser_settings: Source | SourceSettings | SchemaParserSettings | None = None,
        compiler_settings: Source | SourceSettings | CompilerSettings | None = None,
    ) -> Compilation:
        """
        Compile a template with an optional schema.  

        Parameters
        ----------
        template : Source | SourceSettings
            Source or source settings of the template to compile.
        schema : Source | SourceSettings | None
            Optional source or source settings of the schema to use in compilation.
        template_engine : TemplateEngine | Source | SourceSettings | None, optional
            Either a TemplateEngine instance, source settings object or a source pointing to
            template engine settings. If not provided, default configurations are used.
        template_parser_settings : Source | SourceSettings | None
            Optional source or source settings for template parser settings. If not provided, default configurations are used.
        schema_parser_settings : Source | SourceSettings | None
            Optional source or source settings for schema parser settings. If not provided, default configurations are used.
        compiler_settings : Source | SourceSettings | None
            Optional source or source settings for compiler settings. If not provided, default configurations are used.

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

        template_engine_settings_source: Source | None = (
            self._resolve_source(template_engine)
            if isinstance(template_engine, (Source, SourceSettings))
            else None
        )
            
        request: SourceExecutorRequest = SourceExecutorRequest(
            template_source=self._resolve_source(template),
            schema_source=self._resolve_source(schema),
            template_engine_settings_source=template_engine_settings_source,
            template_parser_settings_source=self._resolve_source(template_parser_settings),
            schema_parser_settings_source=self._resolve_source(schema_parser_settings),
            compiler_settings_source=self._resolve_source(compiler_settings)
        )
        result: SourceExecutorResult = self._source_executor.submit(request)
        
        template_engine_to_resolve: TemplateEngine | TemplateEngineSettings | None = (
            template_engine
            if isinstance(template_engine, TemplateEngine)
            else result.template_engine_settings
        )
        template_engine_resolved: TemplateEngine = self._resolve_template_engine(
            template_engine_to_resolve
        )   

        return self._do_compile(result, template_engine_resolved)
            
    # ----------------------------
    # Rendering
    # ----------------------------

    def _render(
            self, 
            compiled: CompilationSpec, 
            result: SourceExecutorResult,
            template_engine: TemplateEngine   
            ) -> Rendering:
        if result.variants_configs is None:
            raise ValueError(f"Missing required variants_configs resolution: {result}")
                
        variants_set: VariantSet = self._loader_facade.load_variants(
            variants_configs=result.variants_configs,
            parser_settings=result.variant_parser_settings
            )
        
        renderer_settings: RendererSettings = (
            self
            ._default_handler
            .renderer_settings_or_default(
                result.renderer_settings
                )
        )
        renderer: Renderer = self._renderer_manager.get_or_create(renderer_settings) 
        
        rendering: Rendering = renderer.render(
            compiled=compiled,
            variants_set=variants_set,
            engine=template_engine
        )
        self._outcome_handler.handle_rendering(rendering)
        return rendering

    def render(
        self, 
        compiled: CompilationSpec,
        variants: Source | SourceSettings | list[Source | SourceSettings],
        *,
        template_engine: TemplateEngine | Source | SourceSettings | None = None,
        variant_parser_settings: Source | SourceSettings | None = None,
        renderer_settings: Source | SourceSettings | None = None,
    ) -> Rendering:
        """
        Render a compiled template using variants and a template engine.

        Parameters
        ----------
        compiled : CompilationSpec
            The compiled template to render.
        variants : Source | SourceSettings | list[Source | SourceSettings]
            Sources or sources settings of variants data.
        template_engine : TemplateEngine | Source | SourceSettings | None, optional
            Either a TemplateEngine instance, source settings object or a source pointing to
            template engine settings. If not provided, default configurations are used.
        variant_parser_settings : Source | SourceSettings | None
            Optional source or source settings for variant parser settings. If not provided, default configurations are used.
        renderer_settings : Source | SourceSettings | None
            Optional source or source settings for renderer settings. If not provided, default configurations are used.

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

        template_engine_settings_source: Source | None = (
            self._resolve_source(template_engine)
            if isinstance(template_engine, (Source, SourceSettings))
            else None
        )
        
        request: SourceExecutorRequest = SourceExecutorRequest(
            variants_sources=self._resolve_sources(variants),
            template_engine_settings_source=template_engine_settings_source,
            variant_parser_settings_source=self._resolve_source(variant_parser_settings),
            renderer_settings_source=self._resolve_source(renderer_settings)
        )
        result: SourceExecutorResult = self._source_executor.submit(request)
        
        template_engine_to_resolve: TemplateEngine | TemplateEngineSettings | None = (
            template_engine
            if isinstance(template_engine, TemplateEngine)
            else result.template_engine_settings
        )
        template_engine_resolved: TemplateEngine = self._resolve_template_engine(
            template_engine_to_resolve
        )   

        return self._render(compiled, result, template_engine_resolved)
    
    # ----------------------------
    # Validation
    # ----------------------------

    def _validate(self, compiled: CompilationSpec, result: SourceExecutorResult) -> Rendering:
        if result.variants_configs is None:
            raise ValueError(f"Missing required variants_configs resolution: {result}")
                
        variants_set: VariantSet = self._loader_facade.load_variants(
            variants_configs=result.variants_configs,
            parser_settings=result.variant_parser_settings
            )
        
        renderer_settings: RendererSettings = (
            self
            ._default_handler
            .renderer_settings_or_default(
                result.renderer_settings
                )
        )
        renderer: Renderer = self._renderer_manager.get_or_create(renderer_settings) 
        
        rendering: Rendering = renderer.validate(
            compiled=compiled,
            variants_set=variants_set,
        )
        self._outcome_handler.handle_validation(rendering)
        return rendering

    def validate(
        self, 
        compiled: CompilationSpec,
        variants: Source | SourceSettings | list[Source | SourceSettings],
        *,
        variant_parser_settings: Source | SourceSettings | None = None,
        renderer_settings: Source | SourceSettings | None = None,
    ) -> Rendering:
        """
        Validate a compiled template against variants without effectively rendering it.

        Parameters
        ----------
        compiled : CompilationSpec
            The compiled template to render.
        variants : Source | SourceSettings | list[Source | SourceSettings]
            Sources or sources settings of variants data.
        variant_parser_settings : Source | SourceSettings | None
            Optional source or source settings for variant parser settings. If not provided, default configurations are used.
        renderer_settings : Source | SourceSettings | None
            Optional source or source settings for renderer settings. If not provided, default configurations are used.

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

        request: SourceExecutorRequest = SourceExecutorRequest(
            variants_sources=self._resolve_sources(variants),
            variant_parser_settings_source=self._resolve_source(variant_parser_settings),
            renderer_settings_source=self._resolve_source(renderer_settings)
        )
        result: SourceExecutorResult = self._source_executor.submit(request)

        return self._validate(compiled, result)

    # ----------------------------
    # Build
    # ----------------------------
    
    def build(
        self, 
        template: Source | SourceSettings,
        variants: Source | SourceSettings | list[Source | SourceSettings],
        schema: Source | SourceSettings | None = None,
        *,
        template_engine: TemplateEngine | Source | SourceSettings | None = None,
        template_parser_settings: Source | SourceSettings | None = None,
        schema_parser_settings: Source | SourceSettings | None = None,
        variant_parser_settings: Source | SourceSettings | None = None,
        compiler_settings: Source | SourceSettings | None = None,
        renderer_settings: Source | SourceSettings | None = None
    ) -> Build:
        """
        Compile, validate and render a template.
        
        Parameters
        ----------
        template : Source | SourceSettings
            Source or source settings of the template to compile.
        variants_sources : Source | SourceSettings | list[Source | SourceSettings]
            Sources or sources settings of variants data.
        schema : Source | SourceSettings | None
            Optional source or source settings of the schema used in compilation.
        template_engine : TemplateEngine | Source | SourceSettings | None, optional
            Either a TemplateEngine instance, source settings object or a source pointing to
            template engine settings. If not provided, default configurations are used.
        schema_parser_settings : Source | SourceSettings | None
            Optional source or source settings for schema parser settings. If not provided, default configurations are used.
        variant_parser_settings : Source | SourceSettings | None
            Optional source or source settings for variant parser settings. If not provided, default configurations are used.
        compiler_settings : Source | SourceSettings | None
            Optional source or source settings for compiler settings. If not provided, default configurations are used.
        renderer_settings: Source | SourceSettings | None
            Optional source or source settings for renderer settings. If not provided, default configurations are used.

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

        template_engine_settings_source: Source | None = (
            self._resolve_source(template_engine)
            if isinstance(template_engine, (Source, SourceSettings))
            else None
        )

        request: SourceExecutorRequest = SourceExecutorRequest(
            template_source=self._resolve_source(template),
            schema_source=self._resolve_source(schema),
            variants_sources=self._resolve_sources(variants),
            template_engine_settings_source=template_engine_settings_source,
            template_parser_settings_source=self._resolve_source(template_parser_settings),
            schema_parser_settings_source=self._resolve_source(schema_parser_settings),
            variant_parser_settings_source=self._resolve_source(variant_parser_settings),
            compiler_settings_source=self._resolve_source(compiler_settings),
            renderer_settings_source=self._resolve_source(renderer_settings)
        )
        result: SourceExecutorResult = self._source_executor.submit(request)
        template_engine_to_resolve: TemplateEngine | TemplateEngineSettings | None = (
            template_engine
            if isinstance(template_engine, TemplateEngine)
            else result.template_engine_settings
        )
        template_engine_resolved: TemplateEngine = self._resolve_template_engine(
            template_engine_to_resolve
        ) 

        compilation: Compilation = self._do_compile(result, template_engine_resolved)
        rendering: Rendering = self._render(compilation.compiled, result, template_engine_resolved)
        return Build(compilation=compilation, rendering=rendering)
