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

    _CONFIG_LOADER_MAP: Mapping[ContentType, type[ConfigParser]] = MappingProxyType(
        {
            ContentType.YAML: YamlParser,
            ContentType.JSON: JsonParser,
            ContentType.TOML: TomlParser,
            ContentType.XML: XmlParser,
        }
    )

    def create(self, content_type: ContentType) -> ConfigParser:
        """Create a `ConfigParser` instance for the given content type."""

        cl_map: Mapping[ContentType, type[ConfigParser]] = self._CONFIG_LOADER_MAP
        if content_type not in cl_map:
            raise UnsopportedConfigError(content_type)
        loader_type: type[ConfigParser] = cl_map[content_type]
        return loader_type()

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class ConfigParserManager:
    """Manages the retrieval of `ConfigParser` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_config_loaders")

    def __init__(
            self, 
            settings: ManagerSettings, 
            factory: ConfigParserFactory | None = None,
            config_loaders: dict[ContentType, ConfigParser] | None = None
            ) -> None:
        
        self._settings: ManagerSettings = settings
        self._factory: ConfigParserFactory = factory or ConfigParserFactory()
        self._config_loaders: dict[ContentType, ConfigParser] = config_loaders or {}
    
    def get_or_create(self, content_type: ContentType) -> ConfigParser:
        """Return a `ConfigParser` instance according to the given content type."""

        l: dict[ContentType, ConfigParser] = self._config_loaders
        if content_type in l:
            return l[content_type]
        
        loader: ConfigParser = self._factory.create(content_type)
        if self._settings.cache:
            l[content_type] = loader
        return loader 

    def __contains__(self, content_type: ContentType) -> bool:
        """Return whether a `ConfigParser` instance for the given content_type is cached."""

        return content_type in self._config_loaders