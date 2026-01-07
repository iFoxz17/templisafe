from abc import ABC
import warnings

from sqltemplater.settings.parser.qparser_settings import QParserSettings
from sqltemplater.util.util import DiagnosticPolicy

class QParser(ABC):
    """Abstract base class for parsers with configurable diagnostic policies."""
    
    __slots__: tuple[str, ...] = ('_settings',)
    
    def __init__(self, settings: QParserSettings) -> None:
        self._settings: QParserSettings = settings

    def _handle_warning(self, warning: Warning) -> None:
        match self._settings.policy:
            case DiagnosticPolicy.ERRORS_ONLY:
                pass
            case DiagnosticPolicy.LOG_WARNINGS:
                warnings.warn(warning, stacklevel=2)
            case DiagnosticPolicy.RAISE_WARNINGS:
                raise warning