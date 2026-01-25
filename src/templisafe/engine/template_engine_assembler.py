from templisafe.engine.template_engine_manager import TemplateEngineFactory, TemplateEngineManager
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
# from templisafe.util.util import DEFAULT_MANAGER_SETTINGS_YAML

DEFAULT_MANAGER_SETTINGS_YAML: str = '''
cache: false
'''

DEFAULT_TEMPLATE_ENGINE_SETTINGS_YAML: str = '''
engine_kind: jinja
config: {}
'''

class TemplateEngineAssembler:
    """Assembles a `TemplateEngineResolver` with all necessary components."""

    __slots__ : tuple[str, ...] = ()

    def assemble(
            self, 
            manager_settings: ManagerSettings | None = None,
            default_template_engine_settings: TemplateEngineSettings | None = None
            ) -> TemplateEngineResolver:
        """
        Create and return a fully initialized `TemplateEngineResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_template_engine_settings : TemplateEngineSettings | None
            Optional engine settings to use as default. If not provided, a default is used.

        Returns
        -------
        TemplateEngineResolver
            A `TemplateEngineResolver` ready to resolve engines.
        """

        factory: TemplateEngineFactory = TemplateEngineFactory()
        manager: TemplateEngineManager = TemplateEngineManager(
            settings=manager_settings or ManagerSettings.from_yaml(DEFAULT_MANAGER_SETTINGS_YAML),
            factory=factory
        )
        resolver: TemplateEngineResolver = TemplateEngineResolver(
            template_engine_manager=manager,
            default_settings=(
                default_template_engine_settings or 
                TemplateEngineSettings.from_yaml(DEFAULT_TEMPLATE_ENGINE_SETTINGS_YAML)
            )
        )

        return resolver
