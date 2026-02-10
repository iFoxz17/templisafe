import pytest
from aiohttp import ClientSession

from templisafe.settings.source.http.http_session_settings import HttpAsyncSessionSettings
from templisafe.source.http.async_.http_async_session_manager import (
    HttpAsyncSessionFactory,
    HttpAsyncSessionManager,
)

@pytest.fixture
def async_settings() -> HttpAsyncSessionSettings:
    return HttpAsyncSessionSettings(
        max_connections=5,
        max_connections_per_host=2,
        force_close=False,
        ttl_dns_cache=60,
    )

@pytest.mark.asyncio
async def test_factory_creates_client_session(async_settings):
    factory = HttpAsyncSessionFactory()
    session = factory.create(async_settings)
    
    assert isinstance(session, ClientSession)
    await session.close()  # cleanup

@pytest.mark.asyncio
async def test_manager_get_or_create_creates_singleton_session(async_settings):
    manager = HttpAsyncSessionManager(async_settings)
    session1 = await manager.get_or_create()
    session2 = await manager.get_or_create()

    assert session1 is session2
    assert isinstance(session1, ClientSession)

    await manager.reset()  # cleanup

@pytest.mark.asyncio
async def test_manager_reset_creates_new_session(async_settings):
    manager = HttpAsyncSessionManager(async_settings)
    session1 = await manager.get_or_create()
    await manager.reset()
    session2 = await manager.get_or_create()

    assert session1 is not session2
    await manager.reset()  # cleanup

@pytest.mark.asyncio
async def test_manager_reset_without_session(async_settings):
    manager = HttpAsyncSessionManager(async_settings)
    # Should not raise an exception
    await manager.reset()
