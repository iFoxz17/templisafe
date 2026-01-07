from sqltemplater.settings.source_settings import LocalSourceSettings, ContentSourceSettings
from sqltemplater.source.source import Source, SourceSettings
from sqltemplater.source.local_source import LocalSource
from sqltemplater.source.content_source import ContentSource, ContentSourceSettings
from sqltemplater.exceptions.source_error import UnsupportedSourceError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SourceFactory:
    _SOURCE_MAP: dict[type[SourceSettings], type[Source]] = {
        ContentSourceSettings: ContentSource,
        LocalSourceSettings: LocalSource,

    }
    
    def create(self, settings: SourceSettings) -> Source:
        source_type: type[Source] | None = SourceFactory._SOURCE_MAP.get(type(settings))
        if source_type is None:
            raise UnsupportedSourceError(settings)
        return source_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SourceManager:
    __slots__ = ("_factory", "_sources")

    def __init__(self, sources: dict[SourceSettings, Source] | None = None) -> None:
        self._factory: SourceFactory = SourceFactory()
        self._sources: dict[SourceSettings, Source] = sources or {}
    
    def get_or_create(self, settings: SourceSettings) -> Source:
        s: dict[SourceSettings, Source] = self._sources
        if settings not in s:
            s[settings] = self._factory.create(settings)
        return s[settings]

    def __contains__(self, settings: SourceSettings) -> bool:
        return settings in self._sources