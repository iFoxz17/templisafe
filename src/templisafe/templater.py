from collections.abc import Iterable
from typing import TypeVar

from templisafe.content.content import Content
from templisafe.default_handler import DefaultHandler
from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.executor.source_executor import (
    SourceExecutor,
    SourceExecutorRequest,
    SourceRequest,
)
from templisafe.executor.source_executor_resolver import SourceExecutorResolver
from templisafe.outcome_handler import OutcomeHandler
from templisafe.parser.config.config_parser import Config
from templisafe.parser.config.config_parser_resolver import ConfigParserResolver
from templisafe.parser.loader_facade import LoaderFacade
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.settings import Settings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.source.source import Source
from templisafe.source.source_resolver import SourceResolver
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_resolver import CompilerResolver
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_resolver import RendererResolver
from templisafe.template.template_model import (
    Build,
    Compilation,
    CompilationSpec,
    Rendering,
    Schema,
    Template,
    VariantSet,
)

S = TypeVar("S", bound=Settings)
SourceInput = Source | SourceSettings
SettingInput = S | SourceInput | None


class Templater:
    """
    Public orchestrator for template workflows.

    The class keeps the user-facing API small while delegating the real work to
    sources, parsers, template engines, compilers and renderers.
    """

    __slots__: tuple[str, ...] = (
        "_source_resolver",
        "_source_executor_resolver",
        "_config_parser_resolver",
        "_template_engine_resolver",
        "_loader_facade",
        "_compiler_resolver",
        "_renderer_resolver",
        "_outcome_handler",
        "_default_handler",
    )

    def __init__(
        self,
        *,
        source_resolver: SourceResolver,
        source_executor_resolver: SourceExecutorResolver,
        config_parser_resolver: ConfigParserResolver,
        template_engine_resolver: TemplateEngineResolver,
        loader_facade: LoaderFacade,
        compiler_resolver: CompilerResolver,
        renderer_resolver: RendererResolver,
        default_handler: DefaultHandler,
        outcome_handler: OutcomeHandler,
    ) -> None:
        self._source_resolver = source_resolver
        self._source_executor_resolver = source_executor_resolver
        self._config_parser_resolver = config_parser_resolver
        self._template_engine_resolver = template_engine_resolver
        self._loader_facade = loader_facade
        self._compiler_resolver = compiler_resolver
        self._renderer_resolver = renderer_resolver
        self._default_handler = default_handler
        self._outcome_handler = outcome_handler

    # ----------------------------
    # Source and config handling
    # ----------------------------

    def _resolve_source(self, source: SourceInput) -> Source:
        return self._source_resolver.resolve(source)

    def _read_sources(
        self,
        sources: dict[str, SourceInput],
        *,
        source_executor_settings: SourceExecutorSettings | None = None,
    ) -> dict[str, Content]:
        resolved = {
            name: self._resolve_source(source)
            for name, source in sources.items()
            if source is not None
        }
        requests = [
            SourceRequest(id=name, source=source)
            for name, source in resolved.items()
        ]
        executor: SourceExecutor = self._source_executor_resolver.resolve(
            source_executor_settings
        )

        opened: list[Source] = []
        try:
            for source in resolved.values():
                source.open()
                opened.append(source)
            result = executor.execute(SourceExecutorRequest(requests=requests))
        finally:
            for source in reversed(opened):
                source.close()

        return {item.id: item.content for item in result.results}

    def _read_source(
        self,
        source: SourceInput,
        *,
        source_executor_settings: SourceExecutorSettings | None = None,
    ) -> Content:
        return self._read_sources(
            {"source": source},
            source_executor_settings=source_executor_settings,
        )["source"]

    def _parse_config(self, content: Content) -> Config:
        parser = self._config_parser_resolver.resolve(content.type_)
        return parser.parse(content.payload)

    def _settings_from_content(
        self,
        content: Content,
        expected_type: type[S],
    ) -> S:
        config = self._parse_config(content)
        if not isinstance(config, dict):
            raise ValueError(
                f"Expected {expected_type.__name__} configuration to be a mapping"
            )

        settings: Settings = (
            Settings.from_dict(config)
            if "kind" in config
            else expected_type.from_dict(config)
        )
        if not isinstance(settings, expected_type):
            raise ValueError(
                f"Expected settings of type {expected_type.__name__}, "
                f"got {type(settings).__name__}"
            )
        return settings

    def _resolve_settings(
        self,
        value: SettingInput[S],
        expected_type: type[S],
        *,
        source_executor_settings: SourceExecutorSettings | None = None,
    ) -> S | None:
        if value is None:
            return None
        if isinstance(value, expected_type):
            return value
        if isinstance(value, (Source, SourceSettings)):
            content = self._read_source(
                value,
                source_executor_settings=source_executor_settings,
            )
            return self._settings_from_content(content, expected_type)
        raise TypeError(
            f"Expected {expected_type.__name__}, Source, SourceSettings or None; "
            f"got {type(value).__name__}"
        )

    def _as_source_list(
        self,
        sources: SourceInput | Iterable[SourceInput],
    ) -> list[SourceInput]:
        if isinstance(sources, (Source, SourceSettings)):
            return [sources]
        return list(sources)

    def _resolve_template_engine(
        self,
        template_engine: TemplateEngine | TemplateEngineSettings | SourceInput | None,
        *,
        source_executor_settings: SourceExecutorSettings | None = None,
    ) -> TemplateEngine:
        if isinstance(template_engine, TemplateEngine):
            return template_engine
        settings = self._resolve_settings(
            template_engine,
            TemplateEngineSettings,
            source_executor_settings=source_executor_settings,
        )
        settings = self._default_handler.template_engine_settings_or_default(settings)
        return self._template_engine_resolver.resolve(settings)

    # ----------------------------
    # Resource loading
    # ----------------------------

    def _load_template(
        self,
        content: Content,
        template_engine: TemplateEngine,
        parser_settings: TemplateParserSettings | None,
    ) -> Template:
        return self._loader_facade.load_template(
            template_str=content.payload,
            template_engine=template_engine,
            parser_settings=parser_settings,
        )

    def _load_schema(
        self,
        content: Content | None,
        parser_settings: SchemaParserSettings | None,
    ) -> Schema | None:
        if content is None:
            return None
        return self._loader_facade.load_schema(
            schema_config=self._parse_config(content),
            parser_settings=parser_settings,
        )

    def _load_variants(
        self,
        contents: list[Content],
        parser_settings: VariantParserSettings | None,
    ) -> VariantSet:
        return self._loader_facade.load_variants(
            variants_configs=[self._parse_config(content) for content in contents],
            parser_settings=parser_settings,
        )

    # ----------------------------
    # Compilation
    # ----------------------------

    def compile(
        self,
        template: SourceInput,
        schema: SourceInput | None = None,
        *,
        template_engine: TemplateEngine | TemplateEngineSettings | SourceInput | None = None,
        source_executor_settings: SettingInput[SourceExecutorSettings] = None,
        template_parser_settings: SettingInput[TemplateParserSettings] = None,
        schema_parser_settings: SettingInput[SchemaParserSettings] = None,
        compiler_settings: SettingInput[CompilerSettings] = None,
    ) -> Compilation:
        source_executor = self._resolve_settings(
            source_executor_settings,
            SourceExecutorSettings,
        )
        contents = self._read_sources(
            {
                "template": template,
                **({"schema": schema} if schema is not None else {}),
            },
            source_executor_settings=source_executor,
        )

        engine = self._resolve_template_engine(
            template_engine,
            source_executor_settings=source_executor,
        )
        template_parser = self._resolve_settings(
            template_parser_settings,
            TemplateParserSettings,
            source_executor_settings=source_executor,
        )
        schema_parser = self._resolve_settings(
            schema_parser_settings,
            SchemaParserSettings,
            source_executor_settings=source_executor,
        )
        compiler_settings_resolved = self._resolve_settings(
            compiler_settings,
            CompilerSettings,
            source_executor_settings=source_executor,
        )
        compiler_settings_resolved = self._default_handler.compiler_settings_or_default(
            compiler_settings_resolved
        )

        template_obj = self._load_template(contents["template"], engine, template_parser)
        schema_obj = self._load_schema(contents.get("schema"), schema_parser)
        compiler: Compiler = self._compiler_resolver.resolve(compiler_settings_resolved)
        compilation = compiler.compile(template_obj, schema_obj)
        self._outcome_handler.handle_compilation(compilation)
        return compilation

    # ----------------------------
    # Rendering
    # ----------------------------

    def render(
        self,
        compiled: CompilationSpec,
        variants: SourceInput | list[SourceInput],
        *,
        template_engine: TemplateEngine | TemplateEngineSettings | SourceInput | None = None,
        source_executor_settings: SettingInput[SourceExecutorSettings] = None,
        variant_parser_settings: SettingInput[VariantParserSettings] = None,
        renderer_settings: SettingInput[RendererSettings] = None,
    ) -> Rendering:
        source_executor = self._resolve_settings(
            source_executor_settings,
            SourceExecutorSettings,
        )
        variant_sources = self._as_source_list(variants)
        contents = self._read_sources(
            {f"variants.{i}": source for i, source in enumerate(variant_sources)},
            source_executor_settings=source_executor,
        )

        engine = self._resolve_template_engine(
            template_engine,
            source_executor_settings=source_executor,
        )
        variant_parser = self._resolve_settings(
            variant_parser_settings,
            VariantParserSettings,
            source_executor_settings=source_executor,
        )
        renderer_settings_resolved = self._resolve_settings(
            renderer_settings,
            RendererSettings,
            source_executor_settings=source_executor,
        )
        renderer_settings_resolved = self._default_handler.renderer_settings_or_default(
            renderer_settings_resolved
        )

        variants_set = self._load_variants(
            [contents[f"variants.{i}"] for i in range(len(variant_sources))],
            variant_parser,
        )
        renderer: Renderer = self._renderer_resolver.resolve(renderer_settings_resolved)
        rendering = renderer.render(compiled, variants_set, engine)
        self._outcome_handler.handle_rendering(rendering)
        return rendering

    # ----------------------------
    # Validation
    # ----------------------------

    def validate(
        self,
        compiled: CompilationSpec,
        variants: SourceInput | list[SourceInput],
        *,
        source_executor_settings: SettingInput[SourceExecutorSettings] = None,
        variant_parser_settings: SettingInput[VariantParserSettings] = None,
        renderer_settings: SettingInput[RendererSettings] = None,
    ) -> Rendering:
        source_executor = self._resolve_settings(
            source_executor_settings,
            SourceExecutorSettings,
        )
        variant_sources = self._as_source_list(variants)
        contents = self._read_sources(
            {f"variants.{i}": source for i, source in enumerate(variant_sources)},
            source_executor_settings=source_executor,
        )
        variant_parser = self._resolve_settings(
            variant_parser_settings,
            VariantParserSettings,
            source_executor_settings=source_executor,
        )
        renderer_settings_resolved = self._resolve_settings(
            renderer_settings,
            RendererSettings,
            source_executor_settings=source_executor,
        )
        renderer_settings_resolved = self._default_handler.renderer_settings_or_default(
            renderer_settings_resolved
        )

        variants_set = self._load_variants(
            [contents[f"variants.{i}"] for i in range(len(variant_sources))],
            variant_parser,
        )
        renderer: Renderer = self._renderer_resolver.resolve(renderer_settings_resolved)
        rendering = renderer.validate(compiled, variants_set)
        self._outcome_handler.handle_validation(rendering)
        return rendering

    # ----------------------------
    # Build
    # ----------------------------

    def build(
        self,
        template: SourceInput,
        variants: SourceInput | list[SourceInput],
        schema: SourceInput | None = None,
        *,
        template_engine: TemplateEngine | TemplateEngineSettings | SourceInput | None = None,
        source_executor_settings: SettingInput[SourceExecutorSettings] = None,
        template_parser_settings: SettingInput[TemplateParserSettings] = None,
        schema_parser_settings: SettingInput[SchemaParserSettings] = None,
        variant_parser_settings: SettingInput[VariantParserSettings] = None,
        compiler_settings: SettingInput[CompilerSettings] = None,
        renderer_settings: SettingInput[RendererSettings] = None,
    ) -> Build:
        compilation = self.compile(
            template=template,
            schema=schema,
            template_engine=template_engine,
            source_executor_settings=source_executor_settings,
            template_parser_settings=template_parser_settings,
            schema_parser_settings=schema_parser_settings,
            compiler_settings=compiler_settings,
        )
        rendering = self.render(
            compiled=compilation.compiled,
            variants=variants,
            template_engine=template_engine,
            source_executor_settings=source_executor_settings,
            variant_parser_settings=variant_parser_settings,
            renderer_settings=renderer_settings,
        )
        return Build(compilation=compilation, rendering=rendering)
