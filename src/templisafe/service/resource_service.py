from typing import cast

from pydantic import BaseModel

from templisafe.content.content import Content
from templisafe.engine.template_engine import TemplateEngine
from templisafe.exceptions.variant_error import IllegalVariantError
from templisafe.input import SchemaInput, TemplateInput, VariantInput, VariantSetInput
from templisafe.parser.config.config_parser import Config
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.task.task import CompilationBundle, RenderingBundle, TaskBundle, TaskType
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.template_model import Binding, Compilation, Rendering, Schema, Template, Variant, VariantSet


class ResourceService:
    """Build domain resources and execute the task-specific domain operation."""

    __slots__: tuple[str, ...] = ("_resource_provider",)

    def __init__(self, resource_provider: ResourceProvider) -> None:
        self._resource_provider = resource_provider

    def process(self, component_bundle: TaskBundle) -> Compilation | Rendering:
        if component_bundle.type is TaskType.COMPILATION:
            if not isinstance(component_bundle, CompilationBundle):
                raise TypeError("Compilation task expected a CompilationBundle")
            return self._compile(component_bundle)

        if component_bundle.type is TaskType.RENDERING:
            if not isinstance(component_bundle, RenderingBundle):
                raise TypeError("Rendering task expected a RenderingBundle")
            return self._render(component_bundle)

        raise ValueError(f"Unsupported resource task type: {component_bundle.type}")

    def _content_payload(self, value: str | Content) -> str:
        if isinstance(value, Content):
            return value.payload
        return value

    def _compile(self, bundle: CompilationBundle) -> Compilation:
        if not isinstance(bundle.template_engine, TemplateEngine):
            raise TypeError("Compilation requires a resolved TemplateEngine")
        if not isinstance(bundle.template_parser_settings, TemplateParser):
            raise TypeError("Compilation requires a resolved TemplateParser")
        if not isinstance(bundle.schema_parser_settings, SchemaParser):
            raise TypeError("Compilation requires a resolved SchemaParser")
        if not isinstance(bundle.compiler_settings, Compiler):
            raise TypeError("Compilation requires a resolved Compiler")

        template = self._provide_template(bundle.template, bundle.template_engine, bundle.template_parser_settings)
        schema = self._provide_schema(bundle.schema_, bundle.schema_parser_settings)
        return self._resource_provider.provide_compilation(template, schema, bundle.compiler_settings)

    def _render(self, bundle: RenderingBundle) -> Rendering:
        if not isinstance(bundle.variant_parser_settings, VariantParser):
            raise TypeError("Rendering requires a resolved VariantParser")
        if not isinstance(bundle.renderer_settings, Renderer):
            raise TypeError("Rendering requires a resolved Renderer")

        variants = self._provide_variants(bundle.variants, bundle.variant_parser_settings)
        if bundle.render:
            if not isinstance(bundle.template_engine, TemplateEngine):
                raise TypeError("Rendering requires a resolved TemplateEngine")
            return self._resource_provider.provide_rendering(
                bundle.compiled,
                variants,
                bundle.template_engine,
                bundle.renderer_settings,
            )
        return self._resource_provider.provide_validation(bundle.compiled, variants, bundle.renderer_settings)

    def _provide_template(
        self,
        template_input: str | Content | TemplateInput | Template,
        engine: TemplateEngine,
        parser: TemplateParser,
    ) -> Template:
        if isinstance(template_input, Template):
            return template_input
        if isinstance(template_input, TemplateInput):
            return self._resource_provider.provide_template(template_input.template, engine, parser)
        if not isinstance(template_input, (str, Content)):
            raise TypeError("Template input must resolve to str, Content, TemplateInput or Template")
        return self._resource_provider.provide_template(self._content_payload(template_input), engine, parser)

    def _provide_schema(
        self,
        schema_input: Config | Content | SchemaInput | Schema | type[BaseModel] | None,
        parser: SchemaParser,
    ) -> Schema | None:
        if schema_input is None or isinstance(schema_input, Schema):
            return schema_input
        if isinstance(schema_input, type) and issubclass(schema_input, BaseModel):
            return Schema(model_cls=schema_input)
        if isinstance(schema_input, SchemaInput):
            return self._resource_provider.provide_schema(schema_input.to_config(), parser)
        if isinstance(schema_input, Content):
            raise TypeError("Schema content must be parsed before ResourceService")
        if not isinstance(schema_input, dict):
            raise TypeError(
                "Schema input must resolve to a configuration mapping, SchemaInput, Schema or BaseModel type"
            )
        return self._resource_provider.provide_schema(schema_input, parser)

    def _create_variant(self, variant_input: VariantInput) -> Variant:
        return Variant(
            name=variant_input.name,
            bindings=[
                Binding(index=index, name=name, value=value)
                for index, (name, value) in enumerate(variant_input.bindings.items())
            ],
        )

    def _create_variants_from_set_input(self, variant_set_input: VariantSetInput) -> list[Variant]:
        return [self._create_variant(variant_input) for variant_input in variant_set_input.normalize("default_1")]

    def _create_variant_set(self, variants: list[Variant]) -> VariantSet:
        names: set[str] = set()
        for variant in variants:
            if variant.name in names:
                raise IllegalVariantError(f"Duplicated variant: {variant.name}")
            names.add(variant.name)
        return VariantSet(variants)

    def _provide_variants(
        self,
        variants_input: Config
        | Content
        | VariantInput
        | VariantSetInput
        | Variant
        | VariantSet
        | list[Config | VariantInput | VariantSetInput | Variant | VariantSet],
        parser: VariantParser,
    ) -> VariantSet:
        if isinstance(variants_input, VariantSet):
            return variants_input
        if isinstance(variants_input, Variant):
            return VariantSet([variants_input])
        if isinstance(variants_input, VariantInput):
            return VariantSet([self._create_variant(variants_input)])
        if isinstance(variants_input, VariantSetInput):
            return self._create_variant_set(self._create_variants_from_set_input(variants_input))
        if isinstance(variants_input, list) and all(isinstance(variant, Variant) for variant in variants_input):
            return VariantSet(cast(list[Variant], variants_input))
        if isinstance(variants_input, list) and not all(isinstance(item, dict) for item in variants_input):
            variants: list[Variant] = []
            config_docs: list[dict] = []
            for item in variants_input:
                if isinstance(item, VariantSet):
                    variants.extend(item.variants)
                elif isinstance(item, Variant):
                    variants.append(item)
                elif isinstance(item, VariantInput):
                    variants.append(self._create_variant(item))
                elif isinstance(item, VariantSetInput):
                    variants.extend(self._create_variants_from_set_input(item))
                elif isinstance(item, dict):
                    config_docs.append(item)
                else:
                    raise TypeError("Variant list items must resolve to configuration mappings or variant inputs")
            if config_docs:
                variants.extend(parser.parse(config_docs).variants)
            return self._create_variant_set(variants)
        if isinstance(variants_input, Content):
            raise TypeError("Variant content must be parsed before ResourceService")
        if not isinstance(variants_input, (dict, list)):
            raise TypeError("Variant input must resolve to a configuration mapping, list or variant input")
        return self._resource_provider.provide_variant(variants_input, parser)
