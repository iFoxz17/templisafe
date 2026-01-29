from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.parser.settings.settings_parser_resolver import SettingsParserResolver
from templisafe.settings.settings import SettingsKind

class SettingsParserProvider:
    """Provides `SettingsParser` instances for a given `SettingsKind`."""
    
    __slots__: tuple[str, ...] = ("_settings_parser_resolver",)

    def __init__(self, settings_parser_resolver: SettingsParserResolver) -> None:
        self._settings_parser_resolver: SettingsParserResolver = settings_parser_resolver

    def provide(self, settings_kind: SettingsKind) -> SettingsParser:
        """
        Provide a `SettingsParser` instance for the given `SettingsKind`.

        Parameters
        ----------
        settings_kind: SettingsKind
            The settings type to retrieve the parser for.

        Returns
        -------
        SettingsParser
            The settings parser instance for the given settings kind.
        """

        return self._settings_parser_resolver.resolve(settings_kind)