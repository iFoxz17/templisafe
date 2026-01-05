from pathlib import Path
from overrides import overrides

from sqltemplater.source.source import Source
from sqltemplater.settings.source_settings import LocalSourceSettings

from sqltemplater.exceptions.source_error import LocalSourceError

class LocalSource(Source):
    def __init__(self, settings: LocalSourceSettings) -> None:
        super().__init__(settings)

    @property
    def path(self) -> Path:
        assert isinstance(self._settings, LocalSourceSettings)
        return Path(self._settings.path)
    
    @overrides
    def read(self) -> str:
        path: Path = self.path
        try:
            with path.open("r") as f:
                return f.read()
        except FileNotFoundError:
            raise LocalSourceError(path)