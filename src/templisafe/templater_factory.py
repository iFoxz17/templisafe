from typing import Callable

from templisafe.templater import Templater

from templisafe.util.util import DiagnosticPolicy

from templisafe.settings.settings import Settings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind

from templisafe.source.source_manager import SourceManager
from templisafe.source.source import Source

from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineManager

from templisafe.loader.loader_facade import LoaderFacade
from templisafe.loader.config.config_loader import ConfigLoader
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader, _INDEX_KEY_KEY
from templisafe.loader.variant.variant_loader import VariantLoader

from templisafe.template.compiler import Compiler
from templisafe.template.renderer import Renderer


class TemplaterFactory:
    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _load_settings(
        source: Source | None,
        *,
        expected_type: type[Settings] | None = None,
    ) -> Settings | None:
        """
        Load settings from a Source using SettingsLoader.
        If expected_type is provided, enforce runtime type safety.
        """
        if source is None:
            return None

        loader: ConfigLoader = ConfigLoader()
        settings: Settings = loader.load_settings(source)

        if expected_type and not isinstance(settings, expected_type):
            raise ValueError(
                f"Expected settings of type {expected_type.__name__}, "
                f"got {type(settings).__name__}"
            )

        return settings

    @staticmethod
    def _create_default_settings(factory: Callable[[], Settings]) -> Settings:
        return factory()

    # ------------------------------------------------------------------
    # Template engine
    # ------------------------------------------------------------------
    def _create_template_engine_settings(
        self,
        source: Source | None,
    ) -> TemplateEngineSettings:
        if source is not None:
            settings = self._load_settings(
                source,
                expected_type=TemplateEngineSettings,
            )
            assert isinstance(settings, TemplateEngineSettings) 
            return settings

        # Programmatic default → use .create()
        return TemplateEngineSettings.create(kind=TemplateEngineKind.JINJA)

    # ------------------------------------------------------------------
    # Loader facade
    # ------------------------------------------------------------------
    def _create_loader_facade(
        self,
        template_engine: TemplateEngine,
        *,
        template_loader_settings_source: Source | None = None,
        schema_loader_settings_source: Source | None = None,
        variant_loader_settings_source: Source | None = None,
    ) -> LoaderFacade:
        template_settings: Settings | None = self._load_settings(
            template_loader_settings_source,
            expected_type=TemplateParserSettings,
        )
        assert template_settings is None or isinstance(template_settings, TemplateParserSettings)

        schema_settings: Settings | None = self._load_settings(schema_loader_settings_source)
        assert schema_settings is None or isinstance(schema_settings, SchemaParserSettings)
        
        variant_settings: Settings | None = self._load_settings(variant_loader_settings_source)
        assert variant_settings is None or isinstance(variant_settings, VariantParserSettings)

        settings_loader: ConfigLoader = ConfigLoader()

        return LoaderFacade(
            config_loader=settings_loader,
            template_loader=TemplateLoader(
                default_engine=template_engine,
                default_settings=template_settings,
            ),
            schema_loader=SchemaLoader(schema_settings),
            variant_loader=VariantLoader(variant_settings),
        )

    # ------------------------------------------------------------------
    # Public factory
    # ------------------------------------------------------------------
    def create(
        self,
        *,
        template_engine_settings_source: Source | None = None,
        template_loader_settings_source: Source | None = None,
        schema_loader_settings_source: Source | None = None,
        variant_loader_settings_source: Source | None = None,
        compiler_settings_source: Source | None = None,
        renderer_settings_source: Source | None = None,
        policy: DiagnosticPolicy | None = None,
    ) -> Templater:
        source_manager = SourceManager()
        template_engine_manager = TemplateEngineManager()

        # Template engine
        engine_settings = self._create_template_engine_settings(
            template_engine_settings_source
        )
        template_engine = template_engine_manager.get_or_create(engine_settings)

        # Loaders
        loader_facade = self._create_loader_facade(
            template_engine,
            template_loader_settings_source=template_loader_settings_source,
            schema_loader_settings_source=schema_loader_settings_source,
            variant_loader_settings_source=variant_loader_settings_source,
        )

        # Compiler
        compiler_settings = (
            self._load_settings(
                compiler_settings_source,
                expected_type=CompilerSettings,
            )
            if compiler_settings_source
            else self._create_default_settings(
                lambda: CompilerSettings.create(index_key=_INDEX_KEY_KEY)
            )
        )
        assert isinstance(compiler_settings, CompilerSettings)
        compiler = Compiler(compiler_settings)

        # Renderer
        renderer_settings = (
            self._load_settings(
                renderer_settings_source,
                expected_type=RendererSettings,
            )
            if renderer_settings_source
            else self._create_default_settings(
                lambda: RendererSettings.create(index_key=_INDEX_KEY_KEY)
            )
        )
        assert isinstance(renderer_settings, RendererSettings)
        renderer = Renderer(template_engine, renderer_settings)

        return Templater(
            source_manager=source_manager,
            template_engine_manager=template_engine_manager,
            loader_facade=loader_facade,
            compiler=compiler,
            renderer=renderer,
            policy=policy or DiagnosticPolicy.LOG,
        )