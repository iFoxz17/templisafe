import pytest
import pytest_asyncio
import requests

from templisafe.source.http_source import HttpSource, _reset_http_session
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError
from templisafe.content.content import ContentType


# ============================================================================
# FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def reset_shared_session_async():
    """Reset the shared HTTP session before and after each async test for isolation."""
    await _reset_http_session()
    yield
    await _reset_http_session()


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
    """Test suite for HttpSource.read() - synchronous operations."""

    def test_reads_json_content(self, requests_mock, json_url):
        """HttpSource.read() returns JSON text from a mocked HTTP API."""
        requests_mock.get(
            json_url,
            json={"hello": "world"},
            status_code=200,
            headers={"Content-Type": "application/json"},
        )

        settings = HttpSourceSettings(url=json_url, content_type=ContentType.JSON)
        source = HttpSource(settings)
        
        content = source.read()
        
        assert content == '{"hello": "world"}'

    def test_reads_html_content(self, requests_mock, html_url):
        """HttpSource.read() returns HTML text from a mocked URL."""
        html_content = "<html><body><h1>Hello World</h1></body></html>"
        
        requests_mock.get(
            html_url,
            text=html_content,
            status_code=200,
            headers={"Content-Type": "text/html"},
        )

        settings = HttpSourceSettings(url=html_url, content_type=ContentType.TEXT)
        source = HttpSource(settings)
        
        content = source.read()
        
        assert content == html_content

    def test_raises_on_404_status(self, requests_mock, json_url):
        """HttpSource.read() raises HttpSourceError when server returns 404."""
        requests_mock.get(json_url, status_code=404)

        settings = HttpSourceSettings(url=json_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        with pytest.raises(HttpSourceError) as exc_info:
            source.read()

        assert exc_info.value.url == json_url
        assert exc_info.value.status_code == 404

    def test_raises_on_connection_error(self, requests_mock):
        """HttpSource.read() raises HttpSourceError on connection failure."""
        error_url = "https://api.example.com/error"
        requests_mock.get(error_url, exc=requests.exceptions.ConnectionError)

        settings = HttpSourceSettings(url=error_url, content_type=ContentType.JSON)
        source = HttpSource(settings)

        with pytest.raises(HttpSourceError) as exc_info:
            source.read()

        assert exc_info.value.url == error_url


# ============================================================================
# ASYNCHRONOUS AREAD TESTS (using aresponses)
# ============================================================================

@pytest.mark.asyncio
class TestHttpSourceAsyncRead:
    """Test suite for HttpSource.aread() - asynchronous operations."""

    async def test_returns_content(self, aresponses, json_url, reset_shared_session_async):
        """HttpSource.aread() returns text from a mocked async API."""
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
        
        content = await source.aread()
        
        assert content == '{"hello": "world"}'

    async def test_raises_on_http_error(self, aresponses, reset_shared_session_async):
        """HttpSource.aread() raises HttpSourceError on HTTP failure."""
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
            await source.aread()

        assert fail_url in str(exc_info.value)