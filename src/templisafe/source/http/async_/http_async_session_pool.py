"""
Asynchronous HTTP session manager and reference-counted session pool.

Supports multiple sessions when the number of concurrent sources exceeds the TCPConnector limit.
"""

from dataclasses import dataclass
import asyncio
import aiohttp
from templisafe.settings.source.http.http_async_session_settings import HttpAsyncSessionSettings

@dataclass(slots=True)
class SessionSlot:
    """Represents one `aiohttp.ClientSession` with a reference count."""
    session: aiohttp.ClientSession
    ref_count: int = 0


class HttpAsyncSessionManager:
    """Factory and owner of a single `aiohttp.ClientSession`."""

    __slots__ = ("_settings", "_session")

    def __init__(self, settings: HttpAsyncSessionSettings, session: aiohttp.ClientSession | None = None) -> None:
        self._settings = settings
        self._session = session

    async def get_or_create(self) -> aiohttp.ClientSession:
        if self._session is None:
            connector = aiohttp.TCPConnector(
                limit=self._settings.max_connections,
                limit_per_host=self._settings.max_connections_per_host,
                force_close=self._settings.force_close,
                ttl_dns_cache=self._settings.ttl_dns_cache,
            )
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def reset(self) -> None:
        if self._session is not None:
            if not self._session.closed:
                await self._session.close()
            self._session = None


class HttpAsyncSessionPool:
    """Pool of aiohttp.ClientSession objects with reference counting and async safety."""

    def __init__(self, manager: HttpAsyncSessionManager, max_users_per_session: int):
        self.manager = manager
        self.max_users = max_users_per_session
        self.slots: list[SessionSlot] = []
        self.lock = asyncio.Lock()

    async def acquire(self) -> aiohttp.ClientSession:
        async with self.lock:
            for slot in self.slots:
                if slot.ref_count < self.max_users:
                    slot.ref_count += 1
                    return slot.session

            # All full → create a new session
            new_session = await self.manager.get_or_create()
            slot = SessionSlot(new_session, ref_count=1)
            self.slots.append(slot)
            return new_session

    async def release(self, session: aiohttp.ClientSession) -> None:
        async with self.lock:
            for slot in self.slots:
                if slot.session is session:
                    slot.ref_count -= 1
                    if slot.ref_count == 0:
                        await self.manager.reset()
                        self.slots.remove(slot)
                    return
