from typing import AsyncGenerator
import warnings
from contextlib import asynccontextmanager
from asyncio import Lock, Semaphore
from aiohttp import ClientSession

from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from templisafe.source.http.async_.http_async_session_manager import HttpAsyncSessionManager
from ..http_session_slot import HttpSessionSlot

class HttpAsyncSessionPool:
    """Asyncio-safe pool of aiohttp.ClientSession objects with reference counting."""

    __slots__: tuple[str, ...] = ("_manager", "_slots", "_max_connections", "_max_slots", "_lock")

    def __init__(
            self, 
            manager: HttpAsyncSessionManager, 
            max_connections: int, 
            max_slots: int | None = None
            ) -> None:
        self._manager: HttpAsyncSessionManager = manager
        self._max_connections: int = max_connections
        self._max_slots: int | None = max_slots
        self._slots: list[HttpSessionSlot[ClientSession]] = []
        self._lock: Lock = Lock()

    @property
    def has_capacity(self) -> bool:
        return self._max_slots is None or len(self._slots) < self._max_slots

    async def acquire(self) -> ClientSession:
        async with self._lock:
            for slot in self._slots:
                if slot.ref_count < self._max_connections:
                    slot.ref_count += 1
                    return slot.session

            #TODO: avoid raising in production
            if not self.has_capacity:
                warnings.warn(f"HTTP sessions overflow: max sessions {self._max_slots}")
                raise HttpSessionOverflowError(self._max_slots)

            new_session: ClientSession = await self._manager.get_or_create()
            slot: HttpSessionSlot[ClientSession] = HttpSessionSlot(new_session, ref_count=1)
            self._slots.append(slot)
            return new_session

    async def release(self, session: ClientSession) -> None:
        async with self._lock:
            for slot in self._slots:
                if slot.session is session:
                    slot.ref_count -= 1
                    if slot.ref_count == 0:
                        await self._manager.reset()
                        self._slots.remove(slot)
                    return

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[ClientSession]:
        s = await self.acquire()
        try:
            yield s
        finally:
            await self.release(s)


class HttpAsyncSessionPoolThrottled(HttpAsyncSessionPool):
    """Async session pool with global concurrency limit using asyncio.Semaphore."""

    __slots__: tuple[str, ...] = ("_semaphore",)

    def __init__(
            self, 
            manager: HttpAsyncSessionManager, 
            max_connections: int,
            max_concurrency: int, 
            max_slots: int | None = None
            ) -> None:
        super().__init__(manager, max_connections, max_slots)
        self._semaphore: Semaphore = Semaphore(max_concurrency)

    async def acquire(self) -> ClientSession:
        await self._semaphore.acquire()
        try:
            return await super().acquire()
        except Exception:
            self._semaphore.release()
            raise

    async def release(self, session: ClientSession) -> None:
        await super().release(session)
        self._semaphore.release()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[ClientSession]:
        s = await self.acquire()
        try:
            yield s
        finally:
            await self.release(s)
