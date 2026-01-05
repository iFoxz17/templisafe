from overrides import overrides

from sqltemplater.source.source import Source
from sqltemplater.settings.source_settings import ContentSourceSettings

class ContentSource(Source):
    def __init__(self, settings: ContentSourceSettings) -> None:
        super().__init__(settings)

    @property
    def content(self) -> str:
        assert isinstance(self._settings, ContentSourceSettings)
        return self._settings.content

    @overrides
    def read(self) -> str:
        return self.content