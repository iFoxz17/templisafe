from enum import Enum

from enum import Enum

class DiagnosticPolicy(str, Enum):
    """
    Policy for handling warnings and errors during compilation, rendering, validation or build.

    Attributes:
        IGNORE:
            Completely ignore warnings and errors.
            - Errors and warnings do not raise exceptions.
            - No logs or warnings are emitted.
        
        LOG:
            Log warnings, raise errors.
            - Errors will raise the corresponding exception, stopping the process.
            - Warnings will be logged using, but execution continues.
        
        STRICT:
            Raise both warnings and errors.
            - Any warning triggers an exception.
            - Errors also trigger an exception.
            - Use this policy when you want maximum strictness and do not want to allow even minor issues.
    """
    IGNORE = "ignore"
    LOG = "log"
    STRICT = "strict"


class ContentType(Enum):
    TEXT = "text"
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"