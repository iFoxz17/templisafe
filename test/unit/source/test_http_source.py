import pytest
import pytest_asyncio
import requests

from templisafe.source.http_source import HttpSource
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError
from templisafe.content.content import ContentType


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def json_url():
    """Standard JSON API URL for tests."""
    return "https://api.example.com/data"


@pytest.fixture
def html_url():
    """Standard HTML page URL for tests."""
    return "https://example.com/page"


# ============================================================================
# SYNCHRONOUS READ TESTS (using requests_mock)
# ============================================================================

class TestHttpSourceSyncRead:
    """Test suite for HttpSource.read() - synchronous operations using context manager."""

    def test_reads_json_content(self, requests_mock, json_url):
        requests_mock.get(
            json_url,
            json={"hello": "world"},
            status_code=200,
            headers={"Content-Type": "application/json"},
        )

        settings = HttpSourceSettings(url=json_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        with source as s:
            content = s.read()
            assert content == '{"hello": "world"}'

    def test_reads_html_content(self, requests_mock, html_url):
        html_content = "<html><body><h1>Hello World</h1></body></html>"
        requests_mock.get(
            html_url,
            text=html_content,
            status_code=200,
            headers={"Content-Type": "text/html"},
        )

        settings = HttpSourceSettings(url=html_url, content_type=ContentType.TEXT)
        source = HttpSource(settings)

        with source as s:
            content = s.read()
            assert content == html_content

    def test_raises_on_404_status(self, requests_mock, json_url):
        requests_mock.get(json_url, status_code=404)
        settings = HttpSourceSettings(url=json_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        with pytest.raises(HttpSourceError) as exc_info:
            with source as s:
                s.read()
        assert exc_info.value.url == json_url

    def test_raises_on_connection_error(self, requests_mock):
        error_url = "https://api.example.com/error"
        requests_mock.get(error_url, exc=requests.exceptions.ConnectionError)
        settings = HttpSourceSettings(url=error_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        with pytest.raises(HttpSourceError) as exc_info:
            with source as s:
                s.read()
        assert exc_info.value.url == error_url


# ============================================================================

@pytest.mark.asyncio
class TestHttpSourceAsyncRead:
    """Test suite for HttpSource.aread() - asynchronous operations using async context manager."""

    async def test_returns_content(self, aresponses, json_url):
        aresponses.add(
            "api.example.com",
            "/data",
            "GET",
            aresponses.Response(
                text='{"hello": "world"}',
                status=200,
                headers={"Content-Type": "application/json"},
            ),
        )

        settings = HttpSourceSettings(url=json_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        async with source as s:
            content = await s.aread()
            assert content == '{"hello": "world"}'

    async def test_raises_on_http_error(self, aresponses):
        fail_url = "https://api.example.com/fail"
        aresponses.add(
            "api.example.com",
            "/fail",
            "GET",
            aresponses.Response(text="Not found", status=404),
        )

        settings = HttpSourceSettings(url=fail_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        with pytest.raises(HttpSourceError) as exc_info:
            async with source as s:
                await s.aread()
        assert fail_url in str(exc_info.value)
