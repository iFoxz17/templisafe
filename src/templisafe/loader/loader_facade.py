from typing import Any

from templisafe.template.template_model import Schema, Template, VariantSet
from templisafe.source.source import Source
from templisafe.settings.settings import Settings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.engine.template_engine import TemplateEngine
from templisafe.loader.config.config_loader import ConfigLoader
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader

class LoaderFacade:
    __slots__: tuple[str, ...] = (
        "_config_loader",
        "_template_loader", 
        "_schema_loader", 
        "_variant_loader"
        )

    def __init__(
            self, 
            config_loader: ConfigLoader,
            template_loader: TemplateLoader,
            schema_loader: SchemaLoader,
            variant_loader: VariantLoader
            ) -> None:
        self._config_loader: ConfigLoader = config_loader
        self._template_loader: TemplateLoader = template_loader
        self._schema_loader: SchemaLoader = schema_loader
        self._variant_loader: VariantLoader = variant_loader

    def load_settings(
            self, 
            settings_source: Source, 
            ) -> Settings:
        return self._config_loader.load_settings(settings_source)

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
        if parser_settings and not isinstance(parser_settings, SchemaParserSettings):
            raise ValueError(f"Wrong schema parser settings provided: {parser_settings}")
        
        schema_config: dict[str, Any] = self._config_loader.load_config(schema_source)
        return self._schema_loader.load(
            schema_config, 
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
        if parser_settings and not isinstance(parser_settings, VariantParserSettings):
            raise ValueError(f"Wrong variant parser settings provided: {parser_settings}")
        
        variants_configs: list[dict[str, Any]] = [
            self._config_loader.load_config(vs)
            for vs in variants_sources
        ]
        return self._variant_loader.load(
            variants_configs, 
            parser_settings
        )