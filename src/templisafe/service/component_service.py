from templisafe.engine.template_engine import TemplateEngine
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.provider.component.component_provider import ComponentProvider
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.task.task import RenderingBundle, TaskBundle
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.renderer.renderer import Renderer


class ComponentService:
    """Resolve parser, engine, compiler and renderer components for a task bundle."""

    __slots__: tuple[str, ...] = ("_component_provider",)

    def __init__(self, component_provider: ComponentProvider) -> None:
        self._component_provider = component_provider

    def process(self, settings_bundle: TaskBundle) -> TaskBundle:
        updates: dict[str, object] = {}

        should_resolve_template_engine = not isinstance(settings_bundle, RenderingBundle) or settings_bundle.render
        if should_resolve_template_engine:
            template_engine = settings_bundle.template_engine
            if not isinstance(template_engine, TemplateEngine):
                if template_engine is not None and not isinstance(template_engine, TemplateEngineSettings):
                    raise TypeError("template_engine must resolve to TemplateEngineSettings or TemplateEngine")
                updates["template_engine"] = self._component_provider.provide_template_engine(template_engine)

        template_parser_value = getattr(settings_bundle, "template_parser_settings", None)
        if not isinstance(template_parser_value, TemplateParser):
            if template_parser_value is not None and not isinstance(template_parser_value, TemplateParserSettings):
                raise TypeError("template_parser_settings must resolve to TemplateParserSettings")
            updates["template_parser_settings"] = self._component_provider.provide_template_parser(
                template_parser_value
            )

        schema_parser_value = getattr(settings_bundle, "schema_parser_settings", None)
        if not isinstance(schema_parser_value, SchemaParser):
            if schema_parser_value is not None and not isinstance(schema_parser_value, SchemaParserSettings):
                raise TypeError("schema_parser_settings must resolve to SchemaParserSettings")
            updates["schema_parser_settings"] = self._component_provider.provide_schema_parser(schema_parser_value)

        variant_parser_value = getattr(settings_bundle, "variant_parser_settings", None)
        if not isinstance(variant_parser_value, VariantParser):
            if variant_parser_value is not None and not isinstance(variant_parser_value, VariantParserSettings):
                raise TypeError("variant_parser_settings must resolve to VariantParserSettings")
            updates["variant_parser_settings"] = self._component_provider.provide_variant_parser(variant_parser_value)

        compiler_value = getattr(settings_bundle, "compiler_settings", None)
        if not isinstance(compiler_value, Compiler):
            if compiler_value is not None and not isinstance(compiler_value, CompilerSettings):
                raise TypeError("compiler_settings must resolve to CompilerSettings")
            updates["compiler_settings"] = self._component_provider.provide_compiler(compiler_value)

        renderer_value = getattr(settings_bundle, "renderer_settings", None)
        if not isinstance(renderer_value, Renderer):
            if renderer_value is not None and not isinstance(renderer_value, RendererSettings):
                raise TypeError("renderer_settings must resolve to RendererSettings")
            updates["renderer_settings"] = self._component_provider.provide_renderer(renderer_value)

        return settings_bundle.model_copy(update=updates)
