from typing import Callable

from templisafe.resolver.source_resolver import SourceResolver
from templisafe.settings.source_resolver_settings import SourceResolverSettings
from templisafe.template.compiler.compiler_manager import CompilerManager
from templisafe.template.renderer.renderer_manager import RendererManager
from templisafe.templater import Templater
from templisafe.outcome_handler import OutcomeHandler

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
from templisafe.resolver.config_loader import ConfigLoader
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader, _INDEX_KEY_KEY
from templisafe.loader.variant.variant_loader import VariantLoader

class TemplaterFactory:
    """
    Factory for creating Templater instances.

    Provides a high-level interface to assemble all components required
    for template processing, including sources, template engines, loaders,
    compilers, renderers and outcome handling. Ensures correct defaults
    and type-safe settings resolution.
    """

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
    # Source resolver
    # ------------------------------------------------------------------
    def _create_source_resolver(
        self,
        source_resolver_settings_source: Source | None = None,
    ) -> SourceResolver:
        
        settings = (
            self._load_settings(
                source_resolver_settings_source,
                expected_type=SourceResolverSettings,
            )
            if source_resolver_settings_source is not None
            else SourceResolverSettings.create()
        )
        assert isinstance(settings, SourceResolverSettings)

        config_loader: ConfigLoader = ConfigLoader()
        return SourceResolver(settings=settings, config_loader=config_loader)

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

        return LoaderFacade(
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
        source_resolver_settings_source: Source | None = None,
        template_engine_settings_source: Source | None = None,
        template_loader_settings_source: Source | None = None,
        schema_loader_settings_source: Source | None = None,
        variant_loader_settings_source: Source | None = None,
        compiler_settings_source: Source | None = None,
        renderer_settings_source: Source | None = None,
        diagnostic_policy: DiagnosticPolicy | str | None = None,
    ) -> Templater:
        """
        Create a fully configured Templater instance.

        Resolves and applies provided or default settings for resolvers, template engines,
        loaders, compilers and renderers. Initializes the outcome handler
        according to the specified diagnostic policy.

        Parameters
        ----------
        source_resolver_settings_source : Source | None
            Optional source for source resolver settings. If not provided, default configurations are used.
        template_engine_settings_source : Source | None
            Optional source for template engine settings. If not provided, default configurations are used.
        template_loader_settings_source : Source | None
            Optional source for template loader settings. If not provided, default configurations are used.
        schema_loader_settings_source : Source | None
            Optional source for schema loader settings. If not provided, default configurations are used.
        variant_loader_settings_source : Source | None
            Optional source for variant loader settings. If not provided, default configurations are used.
        compiler_settings_source : Source | None
            Optional source for compiler settings. If not provided, default configurations are used.
        renderer_settings_source : Source | None
            Optional source for renderer settings. If not provided, default configurations are used.
        diagnostic_policy : DiagnosticPolicy | str | None
            Optional policy controlling how warnings and errors are handled.
            If not provided, the default policy is used.

        Returns
        -------
        Templater
            A ready-to-use Templater instance with all components configured.

        Raises
        ------
        ValueError
            If any provided settings source yields an object of an unexpected type,
            or if the diagnostic policy string is invalid.
        """

        if isinstance(diagnostic_policy, str):
            try:
                diagnostic_policy = DiagnosticPolicy(diagnostic_policy)
            except ValueError as e:
                raise ValueError(f"Invalid diagnostic policy provided: {diagnostic_policy}") from e

        source_manager: SourceManager = SourceManager()
        template_engine_manager: TemplateEngineManager = TemplateEngineManager()
        
        # Source resolver
        source_resolver: SourceResolver = self._create_source_resolver(source_resolver_settings_source)
        
        # Template engine
        engine_settings: TemplateEngineSettings = self._create_template_engine_settings(
            template_engine_settings_source
        )
        template_engine: TemplateEngine = template_engine_manager.get_or_create(engine_settings)

        # Loaders
        loader_facade: LoaderFacade = self._create_loader_facade(
            template_engine,
            template_loader_settings_source=template_loader_settings_source,
            schema_loader_settings_source=schema_loader_settings_source,
            variant_loader_settings_source=variant_loader_settings_source,
        )

        # Compiler
        compiler_settings: Settings | None = (
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
        compiler_manager: CompilerManager = CompilerManager()

        # Renderer
        renderer_settings: Settings | None = (
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
        renderer_manager: RendererManager = RendererManager()

        # Outcome handler
        outcome_handler: OutcomeHandler = OutcomeHandler(policy=diagnostic_policy or DiagnosticPolicy.LOG)

        return Templater(
            source_manager=source_manager,
            source_resolver=source_resolver,
            template_engine_manager=template_engine_manager,
            loader_facade=loader_facade,
            compiler_manager=compiler_manager,
            renderer_manager=renderer_manager,
            outcome_handler=outcome_handler,
            engine_default_settings=engine_settings,
            compiler_default_settings=compiler_settings,
            renderer_default_settings=renderer_settings
        )