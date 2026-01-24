from abc import ABC, abstractmethod

from templisafe.util.util import ContentType
from templisafe.settings.source.source_settings import SourceSettings
    
class Source(ABC):
    """Abstract base class representing a data source."""

    def __init__(self, settings: SourceSettings) -> None:
        self._settings: SourceSettings = settings

    @property
    def content_type(self) -> ContentType:
        assert self._settings.content_type is not None
        return self._settings.content_type

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