from abc import ABC, abstractmethod
from pydantic import BaseModel

from templisafe.util.util import DiagnosticPolicy, ContentType

class ParserSettings(BaseModel, ABC):
    policy: DiagnosticPolicy | None = None

    model_config = {
        "frozen": True
    }

    @property
    @abstractmethod
    def content_type(self) -> ContentType:
        pass