from types import MappingProxyType
from collections.abc import Mapping

from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source import *

from templisafe.source.source import Source
from templisafe.source.inline_source import InlineSource
from templisafe.source.local_source import LocalSource
from templisafe.source.http_source import HttpSource
from templisafe.source.aws import *

from templisafe.exceptions.source_error import UnsupportedSourceError
from templisafe.source.http_source import HttpSource

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SourceFactory:
    _SOURCE_MAP: Mapping[type[SourceSettings], type[Source]] = MappingProxyType(
        {
            InlineSourceSettings: InlineSource,
            LocalSourceSettings: LocalSource,
            HttpSourceSettings: HttpSource,
            AwsS3BucketSourceSettings: AwsS3BucketSource,
            AwsSecretsManagerSourceSettings: AwsSecretsManagerSource,
            AwsSsmParameterSourceSettings: AwsSsmParameterSource,
            AwsDynamoDBSourceSettings: AwsDynamoDBSource
        }
    )
    
    def create(self, settings: SourceSettings) -> Source:
        source_type: type[Source] | None = SourceFactory._SOURCE_MAP.get(type(settings))
        if source_type is None:
            raise UnsupportedSourceError(settings)
        return source_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SourceManager:
    __slots__: tuple[str, ...] = ("_settings", "_factory", "_resolver", "_sources")

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
        s: dict[SourceSettings, Source] = self._sources
        if settings in s:
            return s[settings]
        
        source: Source = self._factory.create(settings)
        if self._settings.cache:
            s[settings] = source
        return source 

    def __contains__(self, settings: SourceSettings) -> bool:
        return settings in self._sources