from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.config.config_parser_manager import (
    ConfigParserFactory,
    ConfigParserManager,
)
from templisafe.parser.config.config_parser_resolver import ConfigParserResolver
from templisafe.settings.manager_settings import ManagerSettings


class ConfigParserAssembler:
    """Assembles a `ConfigParserResolver` with all necessary components."""

    __slots__: tuple[str, ...] = ()

    def assemble(
        self,
        manager_settings: ManagerSettings | None = None,
    ) -> ConfigParserResolver:
        """
        Create and return a fully initialized `ConfigParserResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.

        Returns
        -------
        ConfigParserResolver
            A `ConfigParserResolver` ready to resolve config parsers.
        """

        factory: ConfigParserFactory = ConfigParserFactory()
        manager: ConfigParserManager = ConfigParserManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS, factory=factory
        )
        resolver: ConfigParserResolver = ConfigParserResolver(config_parser_manager=manager)

        return resolver
