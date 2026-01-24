import requests
from overrides import overrides

from templisafe.source.source import Source
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError

class HttpSource(Source):
    """A source implementation that retrieves content from an HTTP URL."""

    def __init__(self, settings: HttpSourceSettings) -> None:
        super().__init__(settings)

    @property
    def url(self) -> str:
        assert isinstance(self._settings, HttpSourceSettings)
        return self._settings.url

    @overrides
    def read(self) -> str:
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise HttpSourceError(self.url) from e
