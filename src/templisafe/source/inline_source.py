from overrides import overrides

from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.source.source import Source


class InlineSource(Source):
    """A proxy source for an inline string."""

    def __init__(self, settings: InlineSourceSettings) -> None:
        super().__init__(settings)

    @property
    def content(self) -> str:
        assert isinstance(self._settings, InlineSourceSettings)
        return self._settings.content

    @overrides
    def read(self) -> str:
        return self.content
