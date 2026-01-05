from dataclasses import dataclass
import logging
from jinja2 import Environment
import warnings

from sqltemplater.util.util import DiagnosticPolicy, ContentType

from sqltemplater.source.source_manager import SourceManager
from sqltemplater.settings.source_settings import SourceSettings
from sqltemplater.source.source import Source

from sqltemplater.exceptions.template_error import UnimplementedTemplateParserError
from sqltemplater.exceptions.compilation_error import CompilationError
from sqltemplater.exceptions.rendering_error import RenderingError

from sqltemplater.loader.loader import LoaderContext
from sqltemplater.loader.loader_facade import LoaderFacade
from sqltemplater.loader.template.template_loader import JinjaTemplateLoaderContext
from sqltemplater.loader.environment.environment_loader import EnvironmentLoader
from sqltemplater.loader.template.template_loader import TemplateLoader
from sqltemplater.loader.schema.schema_loader import SchemaLoader
from sqltemplater.loader.params.params_loader import ParamsLoader

from sqltemplater.query.query_model import (
    CompiledQuery, 
    QueryTemplate, 
    QuerySchema, 
    QueryParameterization,
    BuildOutcome,
    BuildResult
)
from sqltemplater.query.query_compiler import QueryCompiler, CompilationResult
from sqltemplater.query.query_renderer import QueryRenderer, RenderingResult

class SqlTemplaterFactory:
    def create_env_loader(self) -> EnvironmentLoader:
        return EnvironmentLoader()    

    def _create_loader_facade(
        self,
        env: Environment,
        env_loader: EnvironmentLoader,
        template_loader_settings_source: Source | None = None,
        schema_loader_settings_source: Source | None = None,
        params_loader_settings_source: Source | None = None
    ) -> LoaderFacade:
        return LoaderFacade(
            env_loader=env_loader,
            template_loader=TemplateLoader(default_env=env, default_settings_source=template_loader_settings_source),
            schema_loader=SchemaLoader(schema_loader_settings_source),
            params_loader=ParamsLoader(params_loader_settings_source)
        ) 
    
    def create(
            self,
            env_loader_settings_source: Source | None = None,
            template_loader_settings_source: Source | None = None,
            schema_loader_settings_source: Source | None = None,
            params_loader_settings_source: Source | None = None,
            policy: DiagnosticPolicy | None = None
            ) -> SqlTemplater:
        
        source_manager: SourceManager = SourceManager()
        
        env_loader: EnvironmentLoader = EnvironmentLoader(env_loader_settings_source)
        env: Environment = env_loader.load()
        loader_facade: LoaderFacade = LoaderFacade(
            env_loader=env_loader,
            template_loader=TemplateLoader(default_env=env, default_settings_source=template_loader_settings_source),
            schema_loader=SchemaLoader(schema_loader_settings_source),
            params_loader=ParamsLoader(params_loader_settings_source)
        )

        compiler: QueryCompiler = QueryCompiler()
        renderer: QueryRenderer = QueryRenderer(env)
    
        return SqlTemplater(
            source_manager=source_manager,
            loader_facade=loader_facade,
            compiler=compiler,
            renderer=renderer,
            policy=policy or DiagnosticPolicy.LOG_WARNINGS,
            env=env 
        )


class SqlTemplater:
    __slots__ = ("_source_manager", "_loader_facade", "_compiler", "_renderer", "_policy", "_env")
    
    def __init__(
        self,
        source_manager: SourceManager,
        loader_facade: LoaderFacade,
        compiler: QueryCompiler,
        renderer: QueryRenderer,
        policy: DiagnosticPolicy,
        env: Environment | None = None
    ) -> None:
        self._source_manager: SourceManager = source_manager
        self._loader_facade: LoaderFacade = loader_facade
        self._compiler: QueryCompiler = compiler
        self._renderer: QueryRenderer = renderer
        self._policy: DiagnosticPolicy = policy
        self._env: Environment = env or loader_facade.load_environemnt()

    def _resolve_env(self, env_settings_source: Source | SourceSettings | None = None) -> Environment:
        return (
            self._loader_facade.load_environemnt(self._resolve_source(env_settings_source))
            if env_settings_source else self._env
        )

    def _handle_outcome(
        self,
        outcome_obj: CompilationResult | RenderingResult,
        *,
        error_cls: type[Exception],
        success_msg: str,
        warning_msg: str,
        error_msg: str
    ) -> None:
        """
        Handle outcome of compilation or rendering according to policy.
        Raises the appropriate exception if necessary.
        """
        match outcome_obj.outcome:
            case BuildOutcome.SUCCESS:
                logging.debug(success_msg)
            case BuildOutcome.WARNING:
                logging.debug(warning_msg)
                if self._policy is DiagnosticPolicy.RAISE_WARNINGS:
                    raise error_cls(outcome_obj)
                elif self._policy is DiagnosticPolicy.LOG_WARNINGS:
                    warnings.warn(warning_msg, stacklevel=2)
            case BuildOutcome.ERROR:
                logging.debug(error_msg)
                raise error_cls(outcome_obj)

    
    def _resolve_source(self, source_or_settings: Source | SourceSettings | None) -> Source | None:
        if isinstance(source_or_settings, SourceSettings):
            return self._source_manager.get_or_create(source_or_settings)
        return source_or_settings
        
    def compile(
        self, 
        template_source: Source | SourceSettings,
        schema_source: Source | SourceSettings | None = None,
        env_settings_source: Source | SourceSettings | None = None,
        template_parser_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None
    ) -> CompilationResult:
        env: Environment = self._resolve_env(self._resolve_source(env_settings_source))

        match template_source.content_type:
            case ContentType.JINJA:
                context: LoaderContext = JinjaTemplateLoaderContext(env=env)
            case _:
                raise UnimplementedTemplateParserError(template_source.content_type)

        template_actual_source: Source | None = self._resolve_source(template_source)
        assert template_actual_source is not None
        template: QueryTemplate = self._loader_facade.load_template(
            template_source=template_actual_source,
            context=context,
            parser_settings_source=self._resolve_source(template_parser_settings_source)
        )

        schema_actual_source: Source | None = self._resolve_source(schema_source)
        schema: QuerySchema | None = (
            self._loader_facade.load_schema(
                schema_source=schema_actual_source,
                parser_settings_source=self._resolve_source(schema_parser_settings_source)
            )
            if schema_actual_source else None
        )

        compilation: CompilationResult = self._compiler.compile(template=template, schema=schema)

        self._handle_outcome(
            compilation,
            error_cls=CompilationError,
            success_msg="Query compiled successfully",
            warning_msg="Query compiled with warnings",
            error_msg="Query compilation failed"
        )

        return compilation

    # ----------------------------
    # Rendering
    # ----------------------------
    def render(
        self, 
        compiled: CompiledQuery,
        params_source: Source | SourceSettings,
        env_settings_source: Source | SourceSettings | None = None,
        params_parser_settings_source: Source | SourceSettings | None = None
    ) -> RenderingResult:

        params_actual_source: Source | None = self._resolve_source(params_source)
        assert params_actual_source is not None
        parameterizations: QueryParameterization = self._loader_facade.load_params(
            params_source=params_actual_source,
            parser_settings_source=self._resolve_source(params_parser_settings_source)
        )

        env: Environment = self._resolve_env(env_settings_source)
        rendering: RenderingResult = self._renderer.render(
            compiled=compiled, 
            parameterizations=parameterizations, 
            env=env
            )

        self._handle_outcome(
            rendering,
            error_cls=RenderingError,
            success_msg="Query rendered successfully",
            warning_msg="Query rendered with warnings",
            error_msg="Query rendering failed"
        )

        return rendering

    # ----------------------------
    # Validation
    # ----------------------------
    def validate(
        self, 
        compiled: CompiledQuery,
        params_source: Source | SourceSettings,
        params_parser_settings_source: Source | SourceSettings | None = None
    ) -> RenderingResult:

        params_actual_source: Source | None = self._resolve_source(params_source)
        assert params_actual_source is not None
        parameterizations: QueryParameterization = self._loader_facade.load_params(
            params_source=params_actual_source,
            parser_settings_source=self._resolve_source(params_parser_settings_source)
        )

        rendering: RenderingResult = self._renderer.validate(compiled=compiled, parameterizations=parameterizations)

        self._handle_outcome(
            rendering,
            error_cls=RenderingError,
            success_msg="Query validated successfully",
            warning_msg="Query validated with warnings",
            error_msg="Query validation failed"
        )

        return rendering

    # ----------------------------
    # Build
    # ----------------------------
    def build(
        self, 
        template_source: Source | SourceSettings,
        params_source: Source | SourceSettings,
        schema_source: Source | SourceSettings | None = None,
        template_parser_settings_source: Source | SourceSettings | None = None,
        schema_parser_settings_source: Source | SourceSettings | None = None,
        params_parser_settings_source: Source | SourceSettings | None = None,
    ) -> BuildResult:

        compilation: CompilationResult = self.compile(
            template_source=template_source,
            schema_source=schema_source,
            template_parser_settings_source=template_parser_settings_source,
            schema_parser_settings_source=schema_parser_settings_source
        )

        assert compilation.compiled_query is not None

        rendering: RenderingResult = self.render(
            compiled=compilation.compiled_query,
            params_source=params_source,
            params_parser_settings_source=params_parser_settings_source
        )

        return BuildResult(compilation=compilation, rendering=rendering)


