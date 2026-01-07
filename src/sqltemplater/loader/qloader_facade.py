from jinja2 import Environment

from sqltemplater.query.query_model import QSchema, QTemplate, QVariantSet
from sqltemplater.source.source import Source
from sqltemplater.loader.qloader import QLoaderContext
from sqltemplater.loader.environment.environment_loader import EnvironmentLoader
from sqltemplater.loader.template.qtemplate_loader import QTemplateLoader
from sqltemplater.loader.schema.qschema_loader import QSchemaLoader
from sqltemplater.loader.variant.qvariant_loader import QVariantLoader

class QLoaderFacade:
    __slots__: tuple[str, ...] = ("_env_loader", "_qtemplate_loader", "_qschema_loader", "_qvariant_loader")

    def __init__(
            self, 
            env_loader: EnvironmentLoader,
            qtemplate_loader: QTemplateLoader,
            qschema_loader: QSchemaLoader,
            qvariant_loader: QVariantLoader
            ) -> None:
        self._env_loader: EnvironmentLoader = env_loader
        self._qtemplate_loader: QTemplateLoader = qtemplate_loader
        self._qschema_loader: QSchemaLoader = qschema_loader
        self._qvariant_loader: QVariantLoader = qvariant_loader

    def load_environemnt(self, env_settings_source: Source | None = None) -> Environment:
        return self._env_loader.load(env_settings_source)

    def load_template(
            self, 
            template_source: Source, 
            context: QLoaderContext | None = None,
            parser_settings_source: Source | None = None
            ) -> QTemplate:
        return self._qtemplate_loader.load(
            template_source,
            context,
            parser_settings_source
        )

    def load_schema(
            self, 
            schema_source: Source, 
            parser_settings_source: Source | None = None
            ) -> QSchema:
        return self._qschema_loader.load(
            schema_source, 
            parser_settings_source
        )
    
    def load_params(
            self, 
            variants_source: Source, 
            parser_settings_source: Source | None = None
            ) -> QVariantSet:
        return self._qvariant_loader.load(
            variants_source, 
            parser_settings_source
        )