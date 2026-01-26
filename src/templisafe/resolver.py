from typing import Any
from dataclasses import dataclass, fields

from templisafe.engine.template_engine import TemplateEngine
from templisafe.executor.source_executor import SourceExecutor
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.source.source import Source
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.source_resolver import SourceResolver
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.renderer.renderer import Renderer

#---------------------------------------------------------------------------------------------
# Resources resolution
#---------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ResolvedResources:
    template: str | None = None
    variants: list[dict[str, Any]] | None = None
    schema: dict[str, Any] | None = None

    @property
    def resolved(self) -> dict[str, Any]:
        """
        Return a mapping of attribute names to their resolved values,
        including only attributes whose value is not None.
        """
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if getattr(self, field.name) is not None
        }
    
#---------------------------------------------------------------------------------------------
# Components resolution
#---------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ResolvedComponents:
    source_executor: SourceExecutor
    template_engine: TemplateEngine | None = None
    template_parser: TemplateParser | None = None
    schema_parser: SchemaParser | None = None
    variant_parser: VariantParser | None = None
    compiler: Compiler | None = None
    renderer: Renderer | None = None

    @property
    def resolved(self) -> dict[str, Any]:
        """
        Return a mapping of attribute names to their resolved values,
        including only attributes whose value is not None.
        """
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if getattr(self, field.name) is not None
        }

class Resolver:
    __slots__: tuple[str, ...] = (
        "_source_resolver", "_template_engine_resolver",
        "_compiler_manager", "_renderer_manager",
        "_outcome_handler", "_default_handler"
    )
    
    def __init__(
        self,
        source_resolver: SourceResolver,
        template_engine_resolver: TemplateEngineResolver,
        loader_facade: LoaderFacade,
        compiler_manager: CompilerManager,
        renderer_manager: RendererManager,
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

    def resolve_source(self, source: Source | SourceSettings) -> Source:
        return self._source_resolver.resolve(source) 
    
    def resolve_template_engine(
            self, 
            template_engine: TemplateEngineSettings | TemplateEngine
            ) -> TemplateEngine:
        return self._template_engine_resolver.resolve(template_engine)