from types import MappingProxyType
from collections.abc import Mapping

from templisafe.exceptions.config_error import UnsopportedConfigError
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.parser.config.config_parser import *
from templisafe.parser.config.config_parser import ConfigParser
from templisafe.content.content import ContentType

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class ConfigParserFactory:
    """Creates `ConfigParser` instances from content types."""

    _CONFIG_TYPE_MAP: Mapping[ContentType, type[ConfigParser]] = MappingProxyType(
        {
            ContentType.YAML: YamlParser,
            ContentType.JSON: JsonParser,
            ContentType.TOML: TomlParser,
            ContentType.XML: XmlParser,
        }
    )

    def create(self, content_type: ContentType) -> ConfigParser:
        """Create a `ConfigParser` instance for the given content type."""

        cl_map: Mapping[ContentType, type[ConfigParser]] = self._CONFIG_TYPE_MAP
        if content_type not in cl_map:
            raise UnsopportedConfigError(content_type)
        parser_type: type[ConfigParser] = cl_map[content_type]
        return parser_type()

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class ConfigParserManager:
    """Manages the retrieval of `ConfigParser` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_config_parsers")

    def __init__(
            self, 
            settings: ManagerSettings, 
            factory: ConfigParserFactory | None = None,
            config_parsers: dict[ContentType, ConfigParser] | None = None
            ) -> None:
        
        self._settings: ManagerSettings = settings
        self._factory: ConfigParserFactory = factory or ConfigParserFactory()
        self._config_parsers: dict[ContentType, ConfigParser] = config_parsers or {}
    
    def get_or_create(self, content_type: ContentType) -> ConfigParser:
        """Return a `ConfigParser` instance according to the given content type."""

        p: dict[ContentType, ConfigParser] = self._config_parsers
        if content_type in p:
            return p[content_type]
        
        parser: ConfigParser = self._factory.create(content_type)
        if self._settings.cache:
            p[content_type] = parser
        return parser 

    def __contains__(self, content_type: ContentType) -> bool:
        """Return whether a `ConfigParser` instance for the given content type is cached."""

        return content_type in self._config_parsers