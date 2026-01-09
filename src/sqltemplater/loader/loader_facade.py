from jinja2 import Environment

from sqltemplater.template.template_model import Schema, Template, VariantSet
from sqltemplater.source.source import Source
from sqltemplater.loader.loader import LoaderContext
from sqltemplater.loader.environment.environment_loader import EnvironmentLoader
from sqltemplater.loader.template.template_loader import TemplateLoader
from sqltemplater.loader.schema.schema_loader import SchemaLoader
from sqltemplater.loader.variant.variant_loader import VariantLoader

class QLoaderFacade:
    __slots__: tuple[str, ...] = ("_env_loader", "_template_loader", "_schema_loader", "_variant_loader")

    def __init__(
            self, 
            env_loader: EnvironmentLoader,
            template_loader: TemplateLoader,
            schema_loader: SchemaLoader,
            variant_loader: VariantLoader
            ) -> None:
        self._env_loader: EnvironmentLoader = env_loader
        self._template_loader: TemplateLoader = template_loader
        self._schema_loader: SchemaLoader = schema_loader
        self._variant_loader: VariantLoader = variant_loader

    def load_environemnt(self, env_settings_source: Source | None = None) -> Environment:
        return self._env_loader.load(env_settings_source)

    def load_template(
            self, 
            template_source: Source, 
            context: LoaderContext | None = None,
            parser_settings_source: Source | None = None
            ) -> Template:
        return self._template_loader.load(
            template_source,
            context,
            parser_settings_source
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
            variants_source: Source, 
            parser_settings_source: Source | None = None
            ) -> VariantSet:
        return self._variant_loader.load(
            variants_source, 
            parser_settings_source
        )