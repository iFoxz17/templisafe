from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source.source_settings import SourceSettings

from templisafe.source.source import Source
from templisafe.source.factory.source_factory import SourceFactory

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SourceManager:
    """Manages the retrieval of `Source` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_sources")

    def __init__(
            self, 
            settings: ManagerSettings, 
            factory: SourceFactory | None = None,
            sources: dict[SourceSettings, Source] | None = None
            ) -> None:
        
        self._settings: ManagerSettings = settings
        self._factory: SourceFactory = factory or SourceFactory()
        self._sources: dict[SourceSettings, Source] = sources or {}
    
    def get_or_create(self, settings: SourceSettings) -> Source:
        """Return a `Source` instance according to the given settings."""

        s: dict[SourceSettings, Source] = self._sources
        if settings in s:
            return s[settings]
        
        source: Source = self._factory.create(settings)
        if self._settings.cache:
            s[settings] = source
        return source 

    def __contains__(self, settings: SourceSettings) -> bool:
        """Return whether a `Source` instance for the given settings is cached."""

        return settings in self._sources