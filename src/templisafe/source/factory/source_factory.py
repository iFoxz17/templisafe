from types import MappingProxyType
from collections.abc import Mapping

from templisafe.settings.source import *

from templisafe.source.factory.http_source_factory import HttpSourceFactory
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
