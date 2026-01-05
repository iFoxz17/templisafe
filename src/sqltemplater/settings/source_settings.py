from abc import ABC
from dataclasses import dataclass

from sqltemplater.util.util import ContentType

@dataclass(frozen=True, slots=True)
class SourceSettings(ABC):
    content_type: ContentType

@dataclass(frozen=True, slots=True)
class LocalSourceSettings(SourceSettings):
    path: str

@dataclass(frozen=True, slots=True)
class ContentSourceSettings(SourceSettings):
    content: str