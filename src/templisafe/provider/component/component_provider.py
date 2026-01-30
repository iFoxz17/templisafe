from templisafe.engine.template_engine import TemplateEngine
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.provider.component.compiler_provider import CompilerProvider
from templisafe.provider.component.renderer_provider import RendererProvider
from templisafe.provider.component.schema_parser_provider import SchemaParserProvider
from templisafe.provider.component.template_engine_provider import TemplateEngineProvider
from templisafe.provider.component.template_parser_provider import TemplateParserProvider
from templisafe.provider.component.variant_parser_provider import VariantParserProvider
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.renderer.renderer import Renderer

class ComponentProvider:
    """
    Facade delegating component resolution to specialized providers.
    """

    __slots__: tuple[str, ...] = (
        "_template_engine_provider",
        "_template_parser_provider",
        "_schema_parser_provider",
        "_variant_parser_provider",
        "_compiler_provider",
        "_renderer_provider",
    )

    def __init__(
        self,
        template_engine_provider: TemplateEngineProvider,
        template_parser_provider: TemplateParserProvider,
        schema_parser_provider: SchemaParserProvider,
        variant_parser_provider: VariantParserProvider,
        compiler_provider: CompilerProvider,
        renderer_provider: RendererProvider,
    ) -> None:
        self._template_engine_provider: TemplateEngineProvider = template_engine_provider
        self._template_parser_provider: TemplateParserProvider = template_parser_provider
        self._schema_parser_provider: SchemaParserProvider = schema_parser_provider
        self._variant_parser_provider: VariantParserProvider = variant_parser_provider
        self._compiler_provider: CompilerProvider = compiler_provider
        self._renderer_provider: RendererProvider = renderer_provider

    def provide_template_engine(
            self,
            template_engine: TemplateEngine | TemplateEngineSettings | None = None
            ) -> TemplateEngine:
        """Delegates to the designated provider to return a `TemplateEngine` instance."""
        return self._template_engine_provider.provide(template_engine)

    def provide_template_parser(
            self, 
            template_parser: TemplateParserSettings | None = None
            ) -> TemplateParser:
        """Delegates to the designated provider to return a `TemplateParser` instance."""
        return self._template_parser_provider.provide(template_parser)

    def provide_schema_parser(
            self, 
            schema_parser: SchemaParser | SchemaParserSettings | None = None,
            ) -> SchemaParser:
        """Delegates to the designated provider to return a `SchemaParser` instance."""
        return self._schema_parser_provider.provide(schema_parser)

    def provide_variant_parser(
            self, 
            variant_parser: VariantParser | VariantParserSettings | None = None
            ) -> VariantParser:
        """Delegates to the designated provider to return a `VariantParser` instance."""
        return self._variant_parser_provider.provide(variant_parser)

    def provide_compiler(
            self, 
            compiler: Compiler | CompilerSettings | None = None
            ) -> Compiler:
        """Delegates to the designated provider to return a `Compiler` instance."""
        return self._compiler_provider.provide(compiler)

    def provide_renderer(
            self, 
            renderer: Renderer | RendererSettings | None = None
            ) -> Renderer:
        """Delegates to the designated provider to return a `Renderer` instance."""
        return self._renderer_provider.provide(renderer)
