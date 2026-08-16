from templisafe.core.field_selector import FieldSelector
from templisafe.engine.template_engine_assembler import TemplateEngineAssembler
from templisafe.executor.source_executor_assembler import SourceExecutorAssembler
from templisafe.executor.strategy_optimizer import StrategyOptimizer
from templisafe.parser.config.config_parser_assembler import ConfigParserAssembler
from templisafe.parser.schema.schema_parser_assembler import SchemaParserAssembler
from templisafe.parser.schema.schema_parser_defaults import SCHEMA_PARSER_SETTINGS_YAML
from templisafe.parser.settings.settings_parser_assembler import SettingsParserAssembler
from templisafe.parser.template.template_parser_assembler import TemplateParserAssembler
from templisafe.parser.variant.variant_parser_assembler import VariantParserAssembler
from templisafe.provider.component.compiler_provider import CompilerProvider
from templisafe.provider.component.component_provider import ComponentProvider
from templisafe.provider.component.renderer_provider import RendererProvider
from templisafe.provider.component.schema_parser_provider import SchemaParserProvider
from templisafe.provider.component.template_engine_provider import TemplateEngineProvider
from templisafe.provider.component.template_parser_provider import TemplateParserProvider
from templisafe.provider.component.variant_parser_provider import VariantParserProvider
from templisafe.provider.config_parser_provider import ConfigParserProvider
from templisafe.provider.content_provider import ContentProvider
from templisafe.provider.resource.compilation_provider import CompilationProvider
from templisafe.provider.resource.config_provider import ConfigProvider
from templisafe.provider.resource.rendering_provider import RenderingProvider
from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.provider.resource.schema_provider import SchemaProvider
from templisafe.provider.resource.settings_provider import SettingsProvider
from templisafe.provider.resource.template_provider import TemplateProvider
from templisafe.provider.resource.variant_provider import VariantProvider
from templisafe.provider.settings_parser_provider import SettingsParserProvider
from templisafe.provider.source_provider import SourceProvider
from templisafe.service.component_service import ComponentService
from templisafe.service.config_service import ConfigService
from templisafe.service.data_service import DataService
from templisafe.service.resource_service import ResourceService
from templisafe.service.service_orchestrator import ServiceOrchestrator
from templisafe.service.settings_service import SettingsService
from templisafe.service.source_service import SourceService
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.source_strategy_optimizer_settings import StrategyOptimizerSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.source_assembler import SourceAssembler
from templisafe.template.compiler.compiler_assembler import CompilerAssembler
from templisafe.template.renderer.renderer_assembler import RendererAssembler


class ServiceAssembler:
    """Assemble the default task service graph."""

    __slots__: tuple[str, ...] = ()

    def assemble(
        self,
        *,
        source_executor_settings: SourceExecutorSettings | None = None,
        template_engine_settings: TemplateEngineSettings | None = None,
        template_parser_settings: TemplateParserSettings | None = None,
        schema_parser_settings: SchemaParserSettings | None = None,
        variant_parser_settings: VariantParserSettings | None = None,
        compiler_settings: CompilerSettings | None = None,
        renderer_settings: RendererSettings | None = None,
        strategy_optimizer_settings: StrategyOptimizerSettings | None = None,
    ) -> ServiceOrchestrator:
        field_selector = FieldSelector()
        content_type_resolver = ContentTypeResolver()

        source_resolver = SourceAssembler().assemble()
        source_executor_resolver = SourceExecutorAssembler().assemble(
            default_executor_settings=source_executor_settings
        )
        config_parser_resolver = ConfigParserAssembler().assemble()
        settings_parser_resolver = SettingsParserAssembler().assemble()

        template_engine_resolver = TemplateEngineAssembler().assemble(
            default_template_engine_settings=template_engine_settings
        )
        template_parser_resolver = TemplateParserAssembler().assemble(
            default_template_parser_settings=template_parser_settings
        )
        schema_parser_resolver = SchemaParserAssembler().assemble(
            default_schema_parser_settings=(
                schema_parser_settings or SchemaParserSettings.from_yaml(SCHEMA_PARSER_SETTINGS_YAML)
            )
        )
        variant_parser_resolver = VariantParserAssembler().assemble(
            default_variant_parser_settings=variant_parser_settings
        )
        compiler_resolver = CompilerAssembler().assemble(default_compiler_settings=compiler_settings)
        renderer_resolver = RendererAssembler().assemble(default_renderer_settings=renderer_settings)

        source_provider = SourceProvider(source_resolver, content_type_resolver)
        content_provider = ContentProvider(
            source_executor_resolver,
            StrategyOptimizer(strategy_optimizer_settings or StrategyOptimizerSettings()),
        )
        config_parser_provider = ConfigParserProvider(config_parser_resolver)
        settings_parser_provider = SettingsParserProvider(settings_parser_resolver)
        component_provider = ComponentProvider(
            template_engine_provider=TemplateEngineProvider(template_engine_resolver),
            template_parser_provider=TemplateParserProvider(template_parser_resolver),
            schema_parser_provider=SchemaParserProvider(schema_parser_resolver),
            variant_parser_provider=VariantParserProvider(variant_parser_resolver),
            compiler_provider=CompilerProvider(compiler_resolver),
            renderer_provider=RendererProvider(renderer_resolver),
        )
        resource_provider = ResourceProvider(
            config_provider=ConfigProvider(),
            settings_provider=SettingsProvider(),
            template_provider=TemplateProvider(),
            schema_provider=SchemaProvider(),
            variant_provider=VariantProvider(),
            compilation_provider=CompilationProvider(),
            rendering_provider=RenderingProvider(),
        )

        return ServiceOrchestrator(
            source_service=SourceService(source_provider, field_selector),
            data_service=DataService(content_provider, field_selector),
            config_service=ConfigService(config_parser_provider, field_selector, resource_provider),
            settings_service=SettingsService(settings_parser_provider, field_selector, resource_provider),
            component_service=ComponentService(component_provider),
            resource_service=ResourceService(resource_provider),
        )
