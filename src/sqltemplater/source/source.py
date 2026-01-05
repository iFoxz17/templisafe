from abc import ABC, abstractmethod

from sqltemplater.util.util import ContentType
from sqltemplater.settings.source_settings import SourceSettings
    
class Source(ABC):
    def __init__(self, settings: SourceSettings) -> None:
        self._settings: SourceSettings = settings

    @property
    def content_type(self) -> ContentType:
        return self._settings.content_type

    @abstractmethod
    def read(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(settings={self._settings})"