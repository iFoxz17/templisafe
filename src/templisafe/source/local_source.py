from pathlib import Path

from overrides import overrides

from templisafe.exceptions.source_error import LocalSourceError
from templisafe.settings.source.local_source_settings import LocalSourceSettings
from templisafe.source.source import Source


class LocalSource(Source):
    """A source that reads content from a local filesystem file."""

    __slots__: tuple[str, ...] = ()

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
        except FileNotFoundError as e:
            raise LocalSourceError(path) from e
