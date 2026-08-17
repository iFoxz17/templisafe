from templisafe.engine.template_engine import TemplateEngine
from templisafe.parser.config.config_parser import Config, ConfigParser
from templisafe.parser.schema.schema_parser import Schema, SchemaParser
from templisafe.parser.settings.settings_parser import Settings, SettingsParser
from templisafe.parser.template.template_parser import Template, TemplateParser
from templisafe.parser.variant.variant_parser import VariantParser, VariantSet
from templisafe.provider.resource.compilation_provider import CompilationProvider
from templisafe.provider.resource.config_provider import ConfigProvider
from templisafe.provider.resource.rendering_provider import RenderingProvider
from templisafe.provider.resource.schema_provider import SchemaProvider
from templisafe.provider.resource.settings_provider import SettingsProvider
from templisafe.provider.resource.template_provider import TemplateProvider
from templisafe.provider.resource.variant_provider import VariantProvider
from templisafe.template.compiler.compiler import Compilation, Compiler
from templisafe.template.renderer.renderer import Renderer, Rendering
from templisafe.template.template_model import CompilationSpec


class ResourceProvider:
    """
    Facade delegating resource resolution to specialized providers.
    """

    __slots__: tuple[str, ...] = (
        "_config_provider",
        "_settings_provider",
        "_template_provider",
        "_schema_provider",
        "_variant_provider",
        "_compilation_provider",
        "_rendering_provider",
    )

    def __init__(
        self,
        config_provider: ConfigProvider,
        settings_provider: SettingsProvider,
        template_provider: TemplateProvider,
        schema_provider: SchemaProvider,
        variant_provider: VariantProvider,
        compilation_provider: CompilationProvider,
        rendering_provider: RenderingProvider,
    ) -> None:
        self._config_provider: ConfigProvider = config_provider
        self._settings_provider: SettingsProvider = settings_provider
        self._template_provider: TemplateProvider = template_provider
        self._schema_provider: SchemaProvider = schema_provider
        self._variant_provider: VariantProvider = variant_provider
        self._compilation_provider: CompilationProvider = compilation_provider
        self._rendering_provider: RenderingProvider = rendering_provider

    def provide_config(self, payload: str, parser: ConfigParser) -> Config:
        """Delegates to the designated provider to return a `Config` instance."""
        return self._config_provider.provide(payload, parser)

    def provide_settings(self, config: Config, parser: SettingsParser) -> Settings:
        """Delegates to the designated provider to return a `Settings` instance."""
        return self._settings_provider.provide(config, parser)

    def provide_template(self, template_str: str, engine, parser: TemplateParser) -> Template:
        """Delegates to the designated provider to return a `Template` instance."""
        return self._template_provider.provide(template_str, engine, parser)

    def provide_schema(self, config: Config, parser: SchemaParser) -> Schema:
        """Delegates to the designated provider to return a `Schema` instance."""
        return self._schema_provider.provide(config, parser)

    def provide_variant(self, config: Config, parser: VariantParser) -> VariantSet:
        """Delegates to the designated provider to return a `VariantSet` instance."""
        return self._variant_provider.provide(config, parser)

    def provide_compilation(self, template: Template, schema: Schema | None, compiler: Compiler) -> Compilation:
        """Delegates to the designated provider to return a `Compilation` instance."""
        return self._compilation_provider.provide(template, schema, compiler)

    def provide_validation(self, compiled: CompilationSpec, variant_set: VariantSet, renderer: Renderer) -> Rendering:
        """Delegates to the designated provider to return the validation of a `Rendering`  instance."""
        return self._rendering_provider.provide_validation(compiled, variant_set, renderer)

    def provide_rendering(
        self,
        compiled: CompilationSpec,
        variant_set: VariantSet,
        engine: TemplateEngine,
        renderer: Renderer,
    ) -> Rendering:
        """Delegates to the designated provider to return a `Rendering` instance."""
        return self._rendering_provider.provide_rendering(compiled, variant_set, engine, renderer)
