from typing import Any, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

from templisafe.loader.config.config_loader import ConfigLoader
from templisafe.source.source import Source
from templisafe.settings.settings import Settings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.source_loader_settings import SourceLoaderSettings

@dataclass(frozen=True, slots=True)
class SourceLoadInput:
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
class SourceLoadOutput:
    template_str: str | None = None
    schema_config: dict[str, Any] | None = None
    variants_configs: list[dict[str, Any]] | None = None

    template_engine_settings: TemplateEngineSettings | None = None
    template_parser_settings: TemplateParserSettings | None = None
    schema_parser_settings_source: SchemaParserSettings | None = None
    variant_parser_settings_source: VariantParserSettings | None = None
    compiler_settings_source: CompilerSettings | None = None
    renderer_settings_source: RendererSettings | None = None


class SourceLoader:
    __slots__ = ("_settings", "_config_loader")

    def __init__(self, settings: SourceLoaderSettings, config_loader: ConfigLoader | None = None) -> None:
        self._settings = settings
        self._config_loader: ConfigLoader = config_loader or ConfigLoader()

    def _read(self, source: Source | None) -> str | None:
        if source is None:
            return None
        return source.read()

    def _load_config(self, config_source: Source | None) -> dict[str, Any] | None:
        if config_source is None:
            return None
        return self._config_loader.load_config(config_source)
    
    def _load_settings(self, settings_source: Source | None) -> Settings | None:
        if settings_source is None:
            return None
        return self._config_loader.load_settings(settings_source)

    def _load_serial(self, sources: SourceLoadInput) -> SourceLoadOutput:
        context: dict[str, Any] = {}

        context["template_str"] = self._read(sources.template_source)
        context["schema_config"] = self._load_config(sources.schema_source)

        variants_configs: list[dict[str, Any]] | None = None
        if sources.variants_sources is not None:
            variants_configs = []
            for src in sources.variants_sources:
                config: dict[str, Any] | None = self._load_config(src)
                assert config is not None
                variants_configs.append(config)
        context["variants_configs"] = variants_configs

        context["template_engine_settings"] = self._load_settings(
            sources.template_engine_settings_source
        )
        context["template_parser_settings"] = self._read(
            sources.template_parser_settings_source
        )
        context["schema_parser_settings_source"] = self._read(
            sources.schema_parser_settings_source
        )
        context["variant_parser_settings_source"] = self._read(
            sources.variant_parser_settings_source
        )
        context["compiler_settings_source"] = self._read(
            sources.compiler_settings_source
        )
        context["renderer_settings_source"] = self._read(
            sources.renderer_settings_source
        )

        return SourceLoadOutput(**context)

    def _submit_variant_futures(
            self,
            executor: ThreadPoolExecutor,
            variants_sources: list[Source]
            ) -> dict[Future, int]:
        """
        Submit all variant sources to the executor and return a mapping
        from future -> variant index for later reordering.
        """

        future_to_idx: dict[Future, int] = {}
        for idx, src in enumerate(variants_sources):
            future: Future = executor.submit(self._load_config, src)
            future_to_idx[future] = idx
        
        return future_to_idx

    def _collect_variant_results(
            self,
            future_to_idx: dict[Future, int]
            ) -> list[dict[str, Any]]:
        """
        Collect completed variant futures and return a list of results
        in the same order as the input sources.
        """

        if not future_to_idx:
            return []

        results: list[dict[str, Any]] = [{}] * len(future_to_idx)
        for future in as_completed(future_to_idx):
            idx: int = future_to_idx[future]
            results[idx] = future.result()
        return results

    def _load_concurrent(self, sources: SourceLoadInput) -> SourceLoadOutput:
        results: dict[str, Any] = {}

        with ThreadPoolExecutor(max_workers=self._settings.n_threads) as executor:
            def submit(source: Source, load_method: Callable[[Source], Any]) -> Future:
                return executor.submit(load_method, source)

            def resolve_submit(source: Source | None, load_method: Callable[[Source | None], Any]) -> Future | None:
                return submit(source, load_method) if source else None

            # Submit top-level sources
            futures: dict[str, Future | None] = {
                "template_str": resolve_submit(sources.template_source, self._read),
                "schema_config": resolve_submit(sources.schema_source, self._load_config),
                "template_engine_settings": resolve_submit(sources.template_engine_settings_source, self._load_settings),
                "template_parser_settings": resolve_submit(sources.template_parser_settings_source, self._load_settings),
                "schema_parser_settings_source": resolve_submit(sources.schema_parser_settings_source, self._load_settings),
                "variant_parser_settings_source": resolve_submit(sources.variant_parser_settings_source, self._load_settings),
                "compiler_settings_source": resolve_submit(sources.compiler_settings_source, self._load_settings),
                "renderer_settings_source": resolve_submit(sources.renderer_settings_source, self._load_settings),
            }

            # Submit variant futures concurrently with top-level sources
            variants_future_map: dict[Future, int] = self._submit_variant_futures(executor, sources.variants_sources or [])

            # Collect variant
            results["variants_configs"] = self._collect_variant_results(variants_future_map)

            # Collect top-level resources
            for name, future in futures.items():
                if future is not None:
                    results[name] = future.result()

        return SourceLoadOutput(**results)


    
    def load(self, sources: SourceLoadInput) -> SourceLoadOutput:
        if self._settings.concurrent:
            return self._load_concurrent(sources)
        return self._load_serial(sources)
