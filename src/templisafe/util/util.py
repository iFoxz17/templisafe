from enum import Enum

class DiagnosticPolicy(str, Enum):
    IGNORE = "ignore"
    LOG = "log"
    STRICT = "strict"

class ContentType(Enum):
    TEXT = "text"
    YAML = "yaml"
    JSON = "json"