from typing import Any, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

from templisafe.parser.config.config_parser_resolver import ConfigParser
from templisafe.source.source import Source
from templisafe.settings.settings import Settings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings

@dataclass(frozen=True, slots=True)
class SourceExecutorRequest:
    template_source: Source | None = None
    schema_source: Source | None = None
    variants_sources: list[Source] | None = None

    template_engine_settings_source: Source | None = None
    template_parser_settings_source: Source | None = None
    schema_parser_settings_source: Source | None = None
    variant_parser_settings_source: Source | None = None
    compiler_settings_source: Source | None = None
    renderer_settings_source: Source | None = None

@dataclass(frozen=True, slots=True)
class SourceExecutorResult:
    template_str: str | None = None
    schema_config: dict[str, Any] | None = None
    variants_configs: list[dict[str, Any]] | None = None

    template_engine_settings: TemplateEngineSettings | None = None
    template_parser_settings: TemplateParserSettings | None = None
    schema_parser_settings: SchemaParserSettings | None = None
    variant_parser_settings: VariantParserSettings | None = None
    compiler_settings: CompilerSettings | None = None
    renderer_settings: RendererSettings | None = None


class SourceExecutor:
    __slots__ = ("_settings", "_config_loader")

    def __init__(self, settings: SourceExecutorSettings, config_loader: ConfigParser | None = None) -> None:
        self._settings: SourceExecutorSettings = settings
        self._config_loader: ConfigParser = config_loader or ConfigParser()

    def _read_or_none(self, source: Source | None) -> str | None:
        return source.read() if source else None 

    def _load_config_or_none(self, config_source: Source | None) -> dict[str, Any] | None:
        return self._config_loader.load_config(config_source) if config_source else None 
        
    def _load_settings_or_none(self, settings_source: Source | None) -> Settings | None:
        return self._config_loader.load_settings(settings_source) if settings_source else None 
        
    def _execute_serial(self, sources: SourceExecutorRequest) -> SourceExecutorResult:
        context: dict[str, Any] = {}

        context["template_str"] = self._read_or_none(sources.template_source)
        context["schema_config"] = self._load_config_or_none(sources.schema_source)

        variants_configs: list[dict[str, Any]] | None = None
        if sources.variants_sources is not None:
            variants_configs = []
            for src in sources.variants_sources:
                config: dict[str, Any] | None = self._load_config_or_none(src)
                assert config is not None
                variants_configs.append(config)
        context["variants_configs"] = variants_configs

        context["template_engine_settings"] = self._load_settings_or_none(
            sources.template_engine_settings_source
        )
        context["template_parser_settings"] = self._load_settings_or_none(
            sources.template_parser_settings_source
        )
        context["schema_parser_settings"] = self._load_settings_or_none(
            sources.schema_parser_settings_source
        )
        context["variant_parser_settings"] = self._load_settings_or_none(
            sources.variant_parser_settings_source
        )
        context["compiler_settings"] = self._load_settings_or_none(
            sources.compiler_settings_source
        )
        context["renderer_settings"] = self._load_settings_or_none(
            sources.renderer_settings_source
        )

        return SourceExecutorResult(**context)

    def _submit_variant_futures(
            self,
            executor: ThreadPoolExecutor,
            variants_sources: list[Source]
            ) -> dict[Future, int]:

        future_to_idx: dict[Future, int] = {}
        for idx, src in enumerate(variants_sources):
            future: Future = executor.submit(self._load_config_or_none, src)
            future_to_idx[future] = idx
        
        return future_to_idx

    def _collect_variant_results(
            self,
            future_to_idx: dict[Future, int]
            ) -> list[dict[str, Any]] | None :

        if not future_to_idx:
            return None

        results: list[dict[str, Any]] = [{}] * len(future_to_idx)
        for future in as_completed(future_to_idx):
            idx: int = future_to_idx[future]
            results[idx] = future.result()
        return results

    def _execute_concurrent(self, sources: SourceExecutorRequest) -> SourceExecutorResult:
        results: dict[str, Any] = {}

        with ThreadPoolExecutor(max_workers=self._settings.n_threads) as executor:
            def submit(source: Source, load_method: Callable[[Source], Any]) -> Future:
                return executor.submit(load_method, source)

            def resolve_submit(source: Source | None, load_method: Callable[[Source | None], Any]) -> Future | None:
                return submit(source, load_method) if source else None

            # Submit top-level sources
            futures: dict[str, Future | None] = {
                "template_str": resolve_submit(sources.template_source, self._read_or_none),
                "schema_config": resolve_submit(sources.schema_source, self._load_config_or_none),
                "template_engine_settings": resolve_submit(sources.template_engine_settings_source, self._load_settings_or_none),
                "template_parser_settings": resolve_submit(sources.template_parser_settings_source, self._load_settings_or_none),
                "schema_parser_settings": resolve_submit(sources.schema_parser_settings_source, self._load_settings_or_none),
                "variant_parser_settings": resolve_submit(sources.variant_parser_settings_source, self._load_settings_or_none),
                "compiler_settings": resolve_submit(sources.compiler_settings_source, self._load_settings_or_none),
                "renderer_settings": resolve_submit(sources.renderer_settings_source, self._load_settings_or_none),
            }

            # Submit variant futures concurrently with top-level sources
            variants_future_map: dict[Future, int] = self._submit_variant_futures(executor, sources.variants_sources or [])

            # Collect variant
            results["variants_configs"] = self._collect_variant_results(variants_future_map)

            # Collect top-level resources
            for name, future in futures.items():
                if future is not None:
                    results[name] = future.result()

        return SourceExecutorResult(**results)

    def submit(self, request: SourceExecutorRequest) -> SourceExecutorResult:
        """
        Submit all provided sources for execution and return their values.
        
        Depending on the settings, source resolution is performed either
        serially or concurrently using a thread pool.

        Parameters
        ----------
        request : SourceResolutionRequest
            Container object holding all optional input sources to execute.

        Returns
        -------
        SourceResolutionResult
            Container object holding all the loaded resources.

        Raises
        ------
        Exception
            Propagates any exception raised during source reading or
            configuration/settings loading.
        """

        return (
            self._execute_concurrent(request)
            if self._settings.concurrent
            else self._execute_serial(request)
        )
