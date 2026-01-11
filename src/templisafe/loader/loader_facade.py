from templisafe.template.template_model import Schema, Template, VariantSet
from templisafe.source.source import Source
from templisafe.engine.template_engine import TemplateEngine
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader

class LoaderFacade:
    __slots__: tuple[str, ...] = ("_template_loader", "_schema_loader", "_variant_loader")

    def __init__(
            self, 
            template_loader: TemplateLoader,
            schema_loader: SchemaLoader,
            variant_loader: VariantLoader
            ) -> None:
        self._template_loader: TemplateLoader = template_loader
        self._schema_loader: SchemaLoader = schema_loader
        self._variant_loader: VariantLoader = variant_loader

    def load_template(
            self, 
            template_source: Source, 
            engine: TemplateEngine | None = None
            ) -> Template:
        return self._template_loader.load(
            template_source,
            engine
        )

    def load_schema(
            self, 
            schema_source: Source, 
            parser_settings_source: Source | None = None
            ) -> Schema:
        return self._schema_loader.load(
            schema_source, 
            parser_settings_source
        )
    
    def load_variants(
            self, 
            variants_sources: list[Source], 
            parser_settings_source: Source | None = None
            ) -> VariantSet:
        return self._variant_loader.load(
            variants_sources, 
            parser_settings_source
        )