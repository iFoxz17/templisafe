from typing import Any

from templisafe.template.template_model import Schema, Template, VariantSet
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.engine.template_engine import TemplateEngine
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader

class LoaderFacade:
    __slots__: tuple[str, ...] = (
        "_template_loader", 
        "_schema_loader", 
        "_variant_loader"
        )

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
            template_str: str, 
            engine: TemplateEngine | None = None
            ) -> Template:
        return self._template_loader.load(
            template_str,
            engine
        )

    def load_schema(
            self, 
            schema_config: dict[str, Any], 
            parser_settings: SchemaParserSettings | None = None
            ) -> Schema:
        
        return self._schema_loader.load(
            schema_config, 
            parser_settings
        )
    
    def load_variants(
        self,
        variants_configs: list[dict[str, Any]],
        parser_settings: VariantParserSettings | None = None,
    ) -> VariantSet:

        
        return self._variant_loader.load(
            variants_configs,
            parser_settings,
        )
