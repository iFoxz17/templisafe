from enum import Enum
from typing import Any, Union, Iterable

from templisafe.settings.manager_settings import ManagerSettings

DEFAULT_MANAGER_SETTINGS: ManagerSettings = ManagerSettings(cache=True)

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

class DiagnosticLevel(Enum):
    DEBUG = "debug"
    WARNING = "warning"
    ERROR = "error"


def dict_to_frozenset(data: dict[Any, Union[Any, Iterable[Any]]]) -> frozenset[tuple[Any, tuple[Any, ...]]]:
    """
    Convert a dictionary into a frozenset of (key, tuple_of_values) pairs.

    Parameters
    ----------
    data : dict[Any, Any | Iterable[Any]]
        Dictionary to convert. Values can be single items or iterables.

    Returns
    -------
    frozenset[tuple[Any, tuple[Any, ...]]]
        Frozenset of key → tuple(values) pairs.

    Raises
    ------
    TypeError
        If a value is not a single item or an iterable.
    """
    converted = []
    for key, value in data.items():
        if isinstance(value, (list, tuple, set)):
            value_tuple = tuple(value)
        else:
            value_tuple = (value,)
        converted.append((key, value_tuple))
    return frozenset(converted)