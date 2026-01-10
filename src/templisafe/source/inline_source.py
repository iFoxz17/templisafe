from overrides import overrides

from templisafe.source.source import Source
from templisafe.settings.source_settings import InlineSourceSettings

class InlineSource(Source):
    def __init__(self, settings: InlineSourceSettings) -> None:
        super().__init__(settings)

    @property
    def content(self) -> str:
        assert isinstance(self._settings, InlineSourceSettings)
        return self._settings.content

    @overrides
    def read(self) -> str:
        return self.content