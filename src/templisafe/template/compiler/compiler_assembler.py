from templisafe.template.compiler.compiler_manager import CompilerFactory, CompilerManager
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.compiler.compiler_resolver import CompilerResolver
from templisafe.util.util import DEFAULT_MANAGER_SETTINGS_YAML

DEFAULT_COMPILER_SETTINGS_YAML: str = '''
index_key: _index
'''

class CompilerAssembler:
    """Assembles a `CompilerResolver` with all necessary components."""

    __slots__ : tuple[str, ...] = ()

    def assemble(
            self, 
            manager_settings: ManagerSettings | None = None,
            default_compiler_settings: CompilerSettings | None = None
            ) -> CompilerResolver:
        """
        Create and return a fully initialized `CompilerResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_compiler_settings : CompilerSettings | None
            Optional engine settings to use as default. If not provided, a default is used.

        Returns
        -------
        CompilerResolver
            A `CompilerResolver` ready to resolve engines.
        """

        factory: CompilerFactory = CompilerFactory()
        manager: CompilerManager = CompilerManager(
            settings=manager_settings or ManagerSettings.from_yaml(DEFAULT_MANAGER_SETTINGS_YAML),
            factory=factory
        )
        resolver: CompilerResolver = CompilerResolver(
            compiler_manager=manager,
            default_settings=(
                default_compiler_settings or 
                CompilerSettings.from_yaml(DEFAULT_COMPILER_SETTINGS_YAML)
            )
        )

        return resolver
