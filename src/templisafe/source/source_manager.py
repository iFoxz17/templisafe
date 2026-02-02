from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source.source_settings import SourceSettings

from templisafe.source.source import Source

from types import MappingProxyType
from collections.abc import Mapping

from templisafe.settings.source import *

from templisafe.source.http.http_source_factory import HttpSourceFactory
from templisafe.source.source import Source
from templisafe.source.inline_source import InlineSource
from templisafe.source.local_source import LocalSource
from templisafe.source.aws import *

from templisafe.exceptions.source_error import UnsupportedSourceError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SourceFactory:
    """Creates `Source` instances from source settings."""

    __slots__: tuple[str, ...] = ("_http_source_factory",)
        
    _SOURCE_MAP: Mapping[type[SourceSettings], type[Source]] = MappingProxyType(
        {
            InlineSourceSettings: InlineSource,
            LocalSourceSettings: LocalSource,
            # HttpSource delegated to the specific factory
            AwsS3BucketSourceSettings: AwsS3BucketSource,
            AwsSecretsManagerSourceSettings: AwsSecretsManagerSource,
            AwsSsmParameterSourceSettings: AwsSsmParameterSource,
            AwsDynamoDBSourceSettings: AwsDynamoDBSource
        }
    )

    def __init__(self, http_source_factory: HttpSourceFactory | None = None) -> None:
        self._http_source_factory: HttpSourceFactory = http_source_factory or HttpSourceFactory()
    
    def create(self, settings: SourceSettings) -> Source:
        """Create a `Source` instance for the given settings."""

        if isinstance(settings, HttpSourceSettings):
            return self._http_source_factory.create(settings)

        source_type: type[Source] | None = SourceFactory._SOURCE_MAP.get(type(settings))
        if source_type is None:
            raise UnsupportedSourceError(settings)
        return source_type(settings)

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