from dataclasses import dataclass
from enum import Enum


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
