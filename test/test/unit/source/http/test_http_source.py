import time
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import ClientResponse, ClientResponseError, ClientSession
from requests import RequestException, Response, Session

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import HttpSourceError, UninitializedSourceError
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.source.http.async_.http_async_session_pool import HttpAsyncSessionPool
from templisafe.source.http.http_source import HttpSessionPool, HttpSource
from templisafe.source.http.sync.http_sync_session_pool import HttpSyncSessionPool

# -------------------------
# Fixtures
# -------------------------


@pytest.fixture
def mock_sync_pool() -> Mock:
    pool = Mock(spec=HttpSyncSessionPool)
    pool.acquire.side_effect = lambda: Session()
    pool.release.return_value = None
    return pool


@pytest.fixture
def mock_async_pool() -> AsyncMock:
    """Return an async pool with mocked acquire/release."""
    pool = AsyncMock(spec=HttpAsyncSessionPool)

    # Make acquire return a simple AsyncMock instead of real ClientSession
    mock_session = AsyncMock(spec=ClientSession)
    pool.acquire.return_value = mock_session
    pool.release.return_value = AsyncMock()  # release is awaited
    return pool


@pytest.fixture
def mock_session_pool(mock_sync_pool, mock_async_pool) -> HttpSessionPool:
    return HttpSessionPool(sync_pool=mock_sync_pool, async_pool=mock_async_pool)


@pytest.fixture
def mock_settings() -> HttpSourceSettings:
    settings = HttpSourceSettings(
        content_type=ContentType.JSON,
        url="https://example.com",
        timeout=5,
    )
    return settings


@pytest.fixture
def http_source(mock_settings, mock_session_pool) -> HttpSource:
    return HttpSource(settings=mock_settings, session_pool=mock_session_pool)


# -------------------------
# Synchronous flow
# -------------------------


def test_open_and_close_sync(http_source: HttpSource):
    # Open acquires sync session
    http_source.open()
    assert http_source._sync_session is not None

    # Close releases it
    http_source.close()
    assert http_source._sync_session is None
    http_source._session_pool.sync_pool.release.assert_called_once()  # type: ignore


def test_read_success(monkeypatch, http_source: HttpSource):
    http_source.open()
    mock_response = Mock(spec=Response)
    mock_response.text = "hello"
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(http_source._sync_session, "get", lambda url, timeout: mock_response)

    result = http_source.read()
    assert result == "hello"


def test_read_uninitialized(http_source: HttpSource):
    with pytest.raises(UninitializedSourceError):
        http_source.read()


def test_read_raises_http_source_error(monkeypatch, http_source: HttpSource):
    http_source.open()

    def raise_exc(url, timeout):
        raise RequestException("fail")

    monkeypatch.setattr(http_source._sync_session, "get", raise_exc)

    with pytest.raises(HttpSourceError):
        http_source.read()


# -------------------------
# Asynchronous flow
# -------------------------

import asyncio


@pytest.mark.asyncio
async def test_aopen_and_aclose_async(http_source: HttpSource):
    await http_source.aopen()
    assert http_source._async_session is not None

    await http_source.aclose()
    assert http_source._async_session is None
    http_source._session_pool.async_pool.release.assert_awaited_once()  # type: ignore


@pytest.mark.asyncio
async def test_aread_success(monkeypatch, http_source):
    await http_source.aopen()

    # Create a mock response
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.text.return_value = "hello"
    mock_response.raise_for_status.return_value = None  # synchronous method

    # Create a mock async context manager for 'async with'
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_response
    mock_cm.__aexit__.return_value = None

    # Patch 'get' to return the async context manager directly
    monkeypatch.setattr(http_source._async_session, "get", lambda *args, **kwargs: mock_cm)

    # Run
    result = await http_source.aread()
    assert result == "hello"


@pytest.mark.asyncio
async def test_aread_uninitialized(http_source):
    with pytest.raises(UninitializedSourceError):
        await http_source.aread()


@pytest.mark.asyncio
async def test_aread_raises_http_source_error(monkeypatch, http_source: HttpSource):
    await http_source.aopen()

    # Create a mock async context manager
    mock_cm = AsyncMock()
    mock_cm.__aenter__.side_effect = ClientResponseError(
        request_info=None,
        history=(),
        status=500,  # type: ignore
    )
    mock_cm.__aexit__.return_value = None

    # Patch session.get to return the context manager directly
    monkeypatch.setattr(http_source._async_session, "get", lambda *args, **kwargs: mock_cm)

    import pytest

    from templisafe.exceptions.source_error import HttpSourceError

    with pytest.raises(HttpSourceError):
        await http_source.aread()
