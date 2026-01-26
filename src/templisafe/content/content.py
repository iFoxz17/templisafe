from enum import Enum
from dataclasses import dataclass

class ContentType(Enum):
    TEXT = "text"
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    XML = "xml"

@dataclass(frozen=True, slots=True)
class Content:
    payload: str
    type_: ContentType