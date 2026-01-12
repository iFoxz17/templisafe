from templisafe.template.template_model import Schema, Template, VariantSet
from templisafe.source.source import Source
from templisafe.settings.settings import Settings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.parser.schema_parser_settings import SchemaParserSettings
from templisafe.settings.parser.variant_parser_settings import VariantParserSettings
from templisafe.engine.template_engine import TemplateEngine
from templisafe.loader.settings.settings_loader import SettingsLoader
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader

class LoaderFacade:
    __slots__: tuple[str, ...] = (
        "_settings_loader",
        "_template_loader", 
        "_schema_loader", 
        "_variant_loader"
        )

    def __init__(
            self, 
            settings_loader: SettingsLoader,
            template_loader: TemplateLoader,
            schema_loader: SchemaLoader,
            variant_loader: VariantLoader
            ) -> None:
        self._settings_loader: SettingsLoader = settings_loader
        self._template_loader: TemplateLoader = template_loader
        self._schema_loader: SchemaLoader = schema_loader
        self._variant_loader: VariantLoader = variant_loader

    def load_settings(
            self, 
            settings_source: Source, 
            ) -> Settings:
        return self._settings_loader.load(settings_source)

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
        parser_settings: Settings | None = (
            self.load_settings(parser_settings_source)
            if parser_settings_source
            else None
        )
        if not isinstance(parser_settings, SchemaParserSettings):
            raise ValueError(f"Wrong schema parser settings provided: {parser_settings}")
        return self._schema_loader.load(
            schema_source, 
            parser_settings
        )
    
    def load_variants(
            self, 
            variants_sources: list[Source], 
            parser_settings_source: Source | None = None
            ) -> VariantSet:
        parser_settings: Settings | None = (
            self.load_settings(parser_settings_source)
            if parser_settings_source
            else None
        )
        if not isinstance(parser_settings, VariantParserSettings):
            raise ValueError(f"Wrong variant parser settings provided: {parser_settings}")
        return self._variant_loader.load(
            variants_sources, 
            parser_settings
        )