from collections.abc import Mapping
from types import MappingProxyType

from templisafe.parser.settings.settings_parser import *
from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.settings import SettingsKind

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------


class SettingsParserFactory:
    """Creates `SettingsParser` instances from settings kind."""

    _SETTINGS_KIND_MAP: Mapping[SettingsKind, type[SettingsParser]] = MappingProxyType(
        {
            SettingsKind.SOURCE_SETTINGS: SourceSettingsParser,
        }
    )

    def create(self, settings_kind: SettingsKind) -> SettingsParser:
        """Create a `SettingsParser` instance for the given settings kind."""

        sk_map: Mapping[SettingsKind, type[SettingsParser]] = self._SETTINGS_KIND_MAP
        parser_type: type[SettingsParser] = sk_map.get(settings_kind, SettingsParser)
        return parser_type()


# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------


class SettingsParserManager:
    """Manages the retrieval of `SettingsParser` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_settings_parsers")

    def __init__(
        self,
        settings: ManagerSettings,
        factory: SettingsParserFactory | None = None,
        settings_parsers: dict[SettingsKind, SettingsParser] | None = None,
    ) -> None:

        self._settings: ManagerSettings = settings
        self._factory: SettingsParserFactory = factory or SettingsParserFactory()
        self._settings_parsers: dict[SettingsKind, SettingsParser] = settings_parsers or {}

    def get_or_create(self, settings_kind: SettingsKind) -> SettingsParser:
        """Return a `SettingsParser` instance according to the given settings kind."""

        p: dict[SettingsKind, SettingsParser] = self._settings_parsers
        if settings_kind in p:
            return p[settings_kind]

        parser: SettingsParser = self._factory.create(settings_kind)
        if self._settings.cache:
            p[settings_kind] = parser
        return parser

    def __contains__(self, settings_kind: SettingsKind) -> bool:
        """Return whether a `SettingsParser` instance for the given settings kind is cached."""

        return settings_kind in self._settings_parsers
