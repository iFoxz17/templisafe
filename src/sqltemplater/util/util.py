from enum import IntEnum, Enum

class DiagnosticPolicy(IntEnum):
    ERRORS_ONLY = 0
    LOG_WARNINGS = 1
    RAISE_WARNINGS = 2

class ContentType(Enum):
    YAML = "yaml"
    JINJA = "j2"