from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.parser.settings.settings_parser_manager import SettingsParserManager
from templisafe.settings.settings import SettingsKind

class SettingsParserResolver:
    """Resolves `SettingsParser` instances."""

    __slots__: tuple[str, ...] = ("_settings_parser_manager",)

    def __init__(
            self, 
            settings_parser_manager: SettingsParserManager,
            ) -> None:
        self._settings_parser_manager: SettingsParserManager = settings_parser_manager
        
    def resolve(self, settings_kind: SettingsKind) -> SettingsParser:
        """
        Resolve a `SettingsParser` instance for a given settings kind.

        Parameters
        ----------
        settings_kind: SettingsKind
            The settings kind to resolve the settings parser from.

        Returns
        -------
        SettingsParser
            The resolved settings parser instance.
        """

        return self._settings_parser_manager.get_or_create(settings_kind)