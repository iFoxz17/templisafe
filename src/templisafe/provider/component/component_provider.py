from templisafe.provider.component.compiler_provider import CompilerProvider
from templisafe.provider.component.renderer_provider import RendererProvider
from templisafe.provider.component.schema_parser_provider import SchemaParserProvider
from templisafe.provider.component.template_engine_provider import TemplateEngineProvider
from templisafe.provider.component.template_parser_provider import TemplateParserProvider
from templisafe.provider.component.variant_parser_provider import VariantParserProvider


class ComponentProvider:
    """Facade for all the component providers."""

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