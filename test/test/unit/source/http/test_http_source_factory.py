from unittest.mock import Mock

import pytest

from templisafe.content.content import ContentType
from templisafe.settings.source.http.http_session_settings import (
    HttpAsyncSessionSettings,
    HttpSyncSessionSettings,
)
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.source.http.http_source import HttpSource
from templisafe.source.http.http_source_factory import HttpSourceFactory


@pytest.fixture
def mock_sync_settings():
    return HttpSyncSessionSettings(pool_connections=2, pool_maxsize=2, max_slots=5, max_concurrency=None)


@pytest.fixture
def mock_async_settings():
    return HttpAsyncSessionSettings(max_connections=2, max_connections_per_host=1, max_slots=5, max_concurrency=None)


@pytest.fixture
def mock_source_settings(mock_sync_settings, mock_async_settings):
    settings = HttpSourceSettings(
        content_type=ContentType.JSON,
        url="https://example.com",
        sync_session_settings=mock_sync_settings,
        async_session_settings=mock_async_settings,
    )
    return settings


def test_create_http_source(mock_source_settings):
    factory = HttpSourceFactory()
    source = factory.create(mock_source_settings)

    assert isinstance(source, HttpSource)
    assert hasattr(source._session_pool, "sync_pool")
    assert source._session_pool.async_pool is None


@pytest.mark.parametrize("sync_concurrency, async_concurrency", [(None, None), (2, 3)])
def test_create_with_throttled_pools(sync_concurrency, async_concurrency):
    sync_settings = HttpSyncSessionSettings(
        pool_connections=1,
        pool_maxsize=1,
        max_slots=2,
        max_concurrency=sync_concurrency,
    )
    async_settings = HttpAsyncSessionSettings(
        max_connections=2,
        max_connections_per_host=1,
        max_slots=2,
        max_concurrency=async_concurrency,
    )
    source_settings = HttpSourceSettings(
        content_type=ContentType.JSON,
        url="https://example.com",
        sync_session_settings=sync_settings,
        async_session_settings=async_settings,
    )

    factory = HttpSourceFactory()
    source = factory.create(source_settings)

    if sync_concurrency is not None:
        from templisafe.source.http.sync.http_sync_session_pool import (
            HttpSyncSessionPoolThrottled,
        )

        assert isinstance(source._session_pool.sync_pool, HttpSyncSessionPoolThrottled)
    else:
        from templisafe.source.http.sync.http_sync_session_pool import (
            HttpSyncSessionPool,
        )

        assert isinstance(source._session_pool.sync_pool, HttpSyncSessionPool)

    async_manager = Mock()
    async_pool = factory._create_async_pool(async_manager, async_settings)
    if async_concurrency is not None:
        from templisafe.source.http.async_.http_async_session_pool import (
            HttpAsyncSessionPoolThrottled,
        )

        assert isinstance(async_pool, HttpAsyncSessionPoolThrottled)
    else:
        from templisafe.source.http.async_.http_async_session_pool import (
            HttpAsyncSessionPool,
        )

        assert isinstance(async_pool, HttpAsyncSessionPool)
