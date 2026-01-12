from abc import ABC, abstractmethod

from templisafe.util.util import ContentType
from templisafe.settings.settings import Settings

class ParserSettings(Settings, ABC):


    @property
    @abstractmethod
    def kind(self) -> ContentType:
        pass