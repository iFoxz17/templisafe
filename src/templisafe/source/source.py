from abc import ABC, abstractmethod

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import MissingContentTypeError
from templisafe.settings.source.source_settings import SourceSettings
    
class Source(ABC):
    """Abstract base class representing a data source."""

    def __init__(self, settings: SourceSettings) -> None:
        if settings.content_type is None:
            raise MissingContentTypeError(settings)

        self._settings: SourceSettings = settings
        self.content_type: ContentType = settings.content_type
        
    @abstractmethod
    def read(self) -> str:
        """
        Retrieve the content of the source as a string.

        Returns
        -------
        str
            The content of the source.
        """
        pass

class AsyncSource(Source, ABC):
    """Abstract class representing an async data source."""

    def __init__(self, settings: SourceSettings) -> None:
        super().__init__(settings)

    @abstractmethod
    async def aread(self) -> str:
        """
        Asynchronously retrieve the content of the source as a string.

        Returns
        -------
        str
            The content of the source.
        """
        pass