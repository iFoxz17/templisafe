from types import MappingProxyType
from collections.abc import Mapping

from templisafe.exceptions.config_error import UnsopportedConfigError
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.config.config_loader import *
from templisafe.config.config_loader import ConfigLoader
from templisafe.util.util import ContentType

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class ConfigLoaderFactory:
    """Creates `ConfigLoader` instances from content types."""

    _CONFIG_LOADER_MAP: Mapping[ContentType, type[ConfigLoader]] = MappingProxyType(
        {
            ContentType.YAML: YamlConfigLoader,
            ContentType.JSON: JsonConfigLoader,
            ContentType.TOML: TomlConfigLoader,
            ContentType.XML: XmlConfigLoader,
        }
    )

    def create(self, content_type: ContentType) -> ConfigLoader:
        """Create a `ConfigLoader` instance for the given content type."""

        cl_map: Mapping[ContentType, type[ConfigLoader]] = self._CONFIG_LOADER_MAP
        if content_type not in cl_map:
            raise UnsopportedConfigError(content_type)
        loader_type: type[ConfigLoader] = cl_map[content_type]
        return loader_type()

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class ConfigLoaderManager:
    """Manages the retrieval of `ConfigLoader` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_config_loaders")

    def __init__(
            self, 
            settings: ManagerSettings, 
            factory: ConfigLoaderFactory | None = None,
            config_loaders: dict[ContentType, ConfigLoader] | None = None
            ) -> None:
        
        self._settings: ManagerSettings = settings
        self._factory: ConfigLoaderFactory = factory or ConfigLoaderFactory()
        self._config_loaders: dict[ContentType, ConfigLoader] = config_loaders or {}
    
    def get_or_create(self, content_type: ContentType) -> ConfigLoader:
        """Return a `Loader` instance according to the given content type."""

        l: dict[ContentType, ConfigLoader] = self._config_loaders
        if content_type in l:
            return l[content_type]
        
        loader: ConfigLoader = self._factory.create(content_type)
        if self._settings.cache:
            l[content_type] = loader
        return loader 

    def __contains__(self, content_type: ContentType) -> bool:
        """Return whether a `ConfigLoader` instance for the given content_type is cached."""

        return content_type in self._config_loaders