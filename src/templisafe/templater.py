import logging
import warnings
from typing import Any, Iterable

from templisafe.util.util import DiagnosticPolicy, ContentType

from templisafe.settings.source_settings import SourceSettings
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind

from templisafe.source.source_manager import SourceManager
from templisafe.source.source import Source

from templisafe.exceptions.template_error import UnsupportedQTemplateParserError
from templisafe.exceptions.compilation_error import CompilationFailureError
from templisafe.exceptions.rendering_error import RenderingError

from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineManager

from templisafe.loader.loader_facade import LoaderFacade
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader, _INDEX_KEY_KEY
from templisafe.loader.variant.variant_loader import VariantLoader

from templisafe.template.template_model import (
    CompilationSpec, 
    Template, 
    Schema, 
    VariantSet,
    Outcome,
    Compilation,
    Rendering,
    Build
)
from templisafe.template.compiler import Compiler
from templisafe.template.renderer import Renderer


class Templater:
    __slots__: tuple[str, ...] = ("_source_manager", "_template_engine_manager", "_loader_facade", "_compiler", "_renderer", "_policy")
    
    def __init__(
        self,
        source_manager: SourceManager,
        template_engine_manager: TemplateEngineManager,
        loader_facade: LoaderFacade,
        compiler: Compiler,
        renderer: Renderer,
        policy: DiagnosticPolicy
    ) -> None:
        self._source_manager: SourceManager = source_manager
        self._template_engine_manager: TemplateEngineManager = template_engine_manager
        self._loader_facade: LoaderFacade = loader_facade
        self._compiler: Compiler = compiler
        self._renderer: Renderer = renderer
        self._policy: DiagnosticPolicy = policy

    def _handle_outcome(
        self,
        outcome_obj: Compilation | Rendering,
        *,
        error_cls: type[Exception],
        success_msg: str,
        warning_msg: str,
        error_msg: str
    ) -> None:
        """
        Handle outcome of compilation or rendering according to policy.
        Raises the appropriate exception if necessary.
        """
        match outcome_obj.outcome:
            case Outcome.SUCCESS:
                logging.debug(success_msg)
            case Outcome.WARNING:
                logging.debug(warning_msg)
                if self._policy is DiagnosticPolicy.STRICT:
                    raise error_cls(outcome_obj)
                elif self._policy is DiagnosticPolicy.BASE:
                    warnings.warn(warning_msg, stacklevel=2)
            case Outcome.ERROR:
                logging.debug(error_msg)
                raise error_cls(outcome_obj)

    
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
    
    def _resolve_template_engine(self, template_engine_settings_source: Source | None) -> TemplateEngine | None:
        if template_engine_settings_source is None:
            return None
        
        config_str: str = template_engine_settings_source.read()
        template_engine_settings = TemplateEngineSettings.create(config=config_str)
        return self._template_engine_manager.get_or_create(template_engine_settings)
            
        
    def compile(
        self, 
        template_source: Source | SourceSettings,
        schema_source: Source | SourceSettings | None = None,
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None
    ) -> Compilation:
        
        template_actual_source: Source | None = self._resolve_source(template_source)
        assert template_actual_source is not None
        
        template_engine_settings_actual_source: Source | None = self._resolve_source(template_engine_settings_source)
        engine: TemplateEngine | None = self._resolve_template_engine(template_engine_settings_actual_source)
        template: Template = self._loader_facade.load_template(
                template_source=template_actual_source,
                engine=engine
            )

        schema_actual_source: Source | None = self._resolve_source(schema_source)
        schema: Schema | None = (
            self._loader_facade.load_schema(
                schema_source=schema_actual_source,
                parser_settings_source=self._resolve_source(schema_parser_settings_source)
            )
            if schema_actual_source else None
        )

        compilation: Compilation = self._compiler.compile(template=template, schema=schema)

        self._handle_outcome(
            compilation,
            error_cls=CompilationFailureError,
            success_msg="Query compiled successfully",
            warning_msg="Query compiled with warnings",
            error_msg="Query compilation failed"
        )

        return compilation

    # ----------------------------
    # Rendering
    # ----------------------------
    def render(
        self, 
        compiled: CompilationSpec,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        variant_parser_settings_source: Source | SourceSettings | None = None
    ) -> Rendering:

        variants_actual_sources: list[Source] = self._resolve_sources(variants_sources)
        
        parameterizations: VariantSet = self._loader_facade.load_variants(
            variants_sources=variants_actual_sources,
            parser_settings_source=self._resolve_source(variant_parser_settings_source)
        )

        template_engine_settings_actual_source: Source | None = self._resolve_source(template_engine_settings_source)
        engine: TemplateEngine | None = self._resolve_template_engine(template_engine_settings_actual_source)
        
        rendering: Rendering = self._renderer.render(
            compiled=compiled, 
            variants_set=parameterizations, 
            engine=engine
            )

        self._handle_outcome(
            rendering,
            error_cls=RenderingError,
            success_msg="Query rendered successfully",
            warning_msg="Query rendered with warnings",
            error_msg="Query rendering failed"
        )

        return rendering

    # ----------------------------
    # Validation
    # ----------------------------
    def validate(
        self, 
        compiled: CompilationSpec,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        *,
        variant_parser_settings_source: Source | SourceSettings | None = None
    ) -> Rendering:

        variants_actual_sources: list[Source] = self._resolve_sources(variants_sources)
        
        variant_set: VariantSet = self._loader_facade.load_variants(
            variants_sources=variants_actual_sources,
            parser_settings_source=self._resolve_source(variant_parser_settings_source)
        )

        rendering: Rendering = self._renderer.validate(compiled=compiled, variants_set=variant_set)

        self._handle_outcome(
            rendering,
            error_cls=RenderingError,
            success_msg="Query validated successfully",
            warning_msg="Query validated with warnings",
            error_msg="Query validation failed"
        )

        return rendering

    # ----------------------------
    # Build
    # ----------------------------
    def build(
        self, 
        template_source: Source | SourceSettings,
        variants_sources: Source | SourceSettings | list[Source | SourceSettings],
        schema_source: Source | SourceSettings | None = None,
        *,
        template_engine_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None,
        variant_parser_settings_source: Source | SourceSettings | None = None,
    ) -> Build:

        compilation: Compilation = self.compile(
            template_source=template_source,
            schema_source=schema_source,
            template_engine_settings_source=template_engine_settings_source,
            schema_parser_settings_source=schema_parser_settings_source
        )

        assert compilation.compiled is not None

        rendering: Rendering = self.render(
            compiled=compilation.compiled,
            variants_sources=variants_sources,
            template_engine_settings_source=template_engine_settings_source,
            variant_parser_settings_source=variant_parser_settings_source
        )

        return Build(compilation=compilation, rendering=rendering)
    

class TemplaterFactory:
    
    def _create_loader_facade(
        self,
        template_engine: TemplateEngine,
        *,
        template_loader_settings_source: Source | None = None,
        schema_loader_settings_source: Source | None = None,
        variant_loader_settings_source: Source | None = None
    ) -> LoaderFacade:
        return LoaderFacade(
            template_loader=TemplateLoader(default_engine=template_engine, default_settings_source=template_loader_settings_source),
            schema_loader=SchemaLoader(schema_loader_settings_source),
            variant_loader=VariantLoader(variant_loader_settings_source)
        )

    def _create_template_engine_settings(self, template_engine_settings_source: Source | None = None) -> TemplateEngineSettings:
        if template_engine_settings_source is None:
            return TemplateEngineSettings.create(kind=TemplateEngineKind.JINJA)
        
        config_str: str = template_engine_settings_source.read()
        return TemplateEngineSettings.create(config=config_str)
        
    def create(
            self,
            *,
            template_engine_settings_source: Source | None = None,
            template_loader_settings_source: Source | None = None,
            schema_loader_settings_source: Source | None = None,
            variant_loader_settings_source: Source | None = None,
            compiler_settings_source: Source | None = None,
            renderer_settings_source: Source | None = None,
            policy: DiagnosticPolicy | None = None
            ) -> Templater:
        
        source_manager: SourceManager = SourceManager()

        template_engine_manager: TemplateEngineManager = TemplateEngineManager()
        template_engine_settings: TemplateEngineSettings = self._create_template_engine_settings(
            template_engine_settings_source
        )
        
        def_template_engine: TemplateEngine = template_engine_manager.get_or_create(template_engine_settings)

        loader_facade: LoaderFacade = self._create_loader_facade(
            def_template_engine,
            template_loader_settings_source=template_loader_settings_source,
            schema_loader_settings_source=schema_loader_settings_source,
            variant_loader_settings_source=variant_loader_settings_source
            )

        compiler_settings: CompilerSettings = (
            CompilerSettings.from_yaml(compiler_settings_source.read())
            if compiler_settings_source
            else CompilerSettings.create(index_key=_INDEX_KEY_KEY)
        )
        compiler: Compiler = Compiler(compiler_settings)

        renderer_settings: RendererSettings = (
            RendererSettings.from_yaml(renderer_settings_source.read())
            if renderer_settings_source
            else RendererSettings.create(index_key=_INDEX_KEY_KEY)
        )
        renderer: Renderer = Renderer(def_template_engine, renderer_settings)
    
        return Templater(
            source_manager=source_manager,
            template_engine_manager=template_engine_manager,
            loader_facade=loader_facade,
            compiler=compiler,
            renderer=renderer,
            policy=policy or DiagnosticPolicy.BASE,
        )


