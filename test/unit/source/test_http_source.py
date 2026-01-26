import pytest

from templisafe.source.http_source import HttpSource
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError
from templisafe.content.content import ContentType


def test_http_source_reads_json_content(requests_mock):
    """HttpSource.read returns JSON text from a fake HTTP API."""
    url = "https://api.example.com/data"

    requests_mock.get(
        url,
        json={"hello": "world"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    settings = HttpSourceSettings(
        url=url,
        content_type=ContentType.JSON,
    )

    source = HttpSource(settings)
    content = source.read()

    assert content == '{"hello": "world"}'


def test_http_source_http_error_raises(requests_mock):
    """HttpSource.read raises HttpSourceError on HTTP failure."""
    url = "https://api.example.com/fail"

    requests_mock.get(url, status_code=404)

    settings = HttpSourceSettings(
        url=url,
        content_type=ContentType.JSON,
    )

    source = HttpSource(settings)

    with pytest.raises(HttpSourceError) as exc:
        source.read()

    assert url in str(exc.value)

