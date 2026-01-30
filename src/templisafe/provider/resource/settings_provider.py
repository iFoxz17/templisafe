from templisafe.parser.config.config_parser import Config
from templisafe.parser.settings.settings_parser import Settings, SettingsParser

class SettingsProvider:
    """Provides `Settings` instances by delegating parsing to a `SettingsParser`."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide(self, config: Config, parser: SettingsParser) -> Settings:
        """
        Parse the given `Config` into a `Settings` using the supplied parser.

        Parameters
        ----------
        config: Config
            The configuration to parse.
        parser: SettingsParser
            The parser responsible for interpreting the configuration.

        Returns
        -------
        Settings
            The parsed settings object.
        """

        return parser.parse(config)
