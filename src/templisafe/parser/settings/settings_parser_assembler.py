from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.settings.settings_parser_manager import (
    SettingsParserFactory,
    SettingsParserManager,
)
from templisafe.parser.settings.settings_parser_resolver import SettingsParserResolver
from templisafe.settings.manager_settings import ManagerSettings


class SettingsParserAssembler:
    """Assembles a `SettingsParserResolver` with all necessary components."""

    __slots__: tuple[str, ...] = ()

    def assemble(
        self,
        manager_settings: ManagerSettings | None = None,
    ) -> SettingsParserResolver:
        """
        Create and return a fully initialized `SettingsParserResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.

        Returns
        -------
        SettingsParserResolver
            A `SettingsParserResolver` ready to resolve settings parsers.
        """

        factory: SettingsParserFactory = SettingsParserFactory()
        manager: SettingsParserManager = SettingsParserManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS, factory=factory
        )
        resolver: SettingsParserResolver = SettingsParserResolver(settings_parser_manager=manager)

        return resolver
