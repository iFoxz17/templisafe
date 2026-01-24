from enum import Enum

class DiagnosticPolicy(str, Enum):
    """
    Policy for handling warnings and errors during compilation, rendering, validation or build.

    Attributes:
        IGNORE:
            Completely ignore warnings and errors.
            - Errors and warnings do not raise exceptions.
            - No logs or warnings are emitted.
            - To use when programmatic access to the build diagnostics is needed.
        
        LOG:
            Log warnings, raise errors.
            - Errors will raise the corresponding exception, stopping the build process.
            - Warnings will be logged, but execution continues.
        
        STRICT:
            Raise both warnings and errors.
            - Any warning triggers an exception.
            - Any error trigger an exception.
    """
    IGNORE = "ignore"
    LOG = "log"
    STRICT = "strict"


class ContentType(Enum):
    TEXT = "text"
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    XML = "xml"

DEFAULT_MANAGER_SETTINGS_YAML: str = '''
cache: true
'''