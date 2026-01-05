from abc import ABC
import warnings

from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.util.util import DiagnosticPolicy

class Parser(ABC):
    
    __slots__ = ('_settings')
    
    def __init__(self, settings: ParserSettings) -> None:
        self._settings: ParserSettings = settings

    def _handle_warning(self, warning: Warning) -> None:
        match self._settings.policy:
            case DiagnosticPolicy.ERRORS_ONLY:
                pass
            case DiagnosticPolicy.LOG_WARNINGS:
                warnings.warn(warning, stacklevel=2)
            case DiagnosticPolicy.RAISE_WARNINGS:
                raise warning