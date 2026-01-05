from jinja2 import Environment

from sqltemplater.query.query_model import QuerySchema, QueryTemplate, QueryParameterization
from sqltemplater.source.source import Source
from sqltemplater.loader.loader import LoaderContext
from sqltemplater.loader.environment.environment_loader import EnvironmentLoader
from sqltemplater.loader.template.template_loader import TemplateLoader
from sqltemplater.loader.schema.schema_loader import SchemaLoader
from sqltemplater.loader.params.params_loader import ParamsLoader

class LoaderFacade:
    __slots__ = ("_env_loader", "_template_loader", "_schema_loader", "_params_loader")

    def __init__(
            self, 
            env_loader: EnvironmentLoader,
            template_loader: TemplateLoader,
            schema_loader: SchemaLoader,
            params_loader: ParamsLoader
            ) -> None:
        self._env_loader: EnvironmentLoader = env_loader
        self._template_loader: TemplateLoader = template_loader
        self._schema_loader: SchemaLoader = schema_loader
        self._params_loader: ParamsLoader = params_loader

    def load_environemnt(self, env_settings_source: Source | None = None) -> Environment:
        return self._env_loader.load(env_settings_source)

    def load_template(
            self, 
            template_source: Source, 
            context: LoaderContext | None = None,
            parser_settings_source: Source | None = None
            ) -> QueryTemplate:
        return self._template_loader.load(
            template_source,
            context,
            parser_settings_source
        )

    def load_schema(
            self, 
            schema_source: Source, 
            parser_settings_source: Source | None = None
            ) -> QuerySchema:
        return self._schema_loader.load(
            schema_source, 
            parser_settings_source
        )
    
    def load_params(
            self, 
            params_source: Source, 
            parser_settings_source: Source | None = None
            ) -> QueryParameterization:
        return self._params_loader.load(
            params_source, 
            parser_settings_source
        )