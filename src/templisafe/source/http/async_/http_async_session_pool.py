import logging
from asyncio import Lock, Semaphore
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiohttp import ClientSession

from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from templisafe.handler.diagnostic_handler import DiagnosticHandler
from templisafe.source.http.async_.http_async_session_manager import (
    HttpAsyncSessionManager,
)

from ..http_session_slot import HttpSessionSlot

logger = logging.getLogger(__name__)


class HttpAsyncSessionPool:
    """
    Asyncio-safe pool of `aiohttp.ClientSession` objects with reference counting.

    This pool allows multiple coroutines to share a limited number of HTTP sessions
    efficiently. Each session has a configurable maximum number of concurrent users
    (`max_connections`). New sessions are created automatically up to `max_slots`
    if all existing sessions are fully used.
    """

    __slots__: tuple[str, ...] = (
        "_manager",
        "_slots",
        "_max_connections",
        "_max_slots",
        "_lock",
    )

    def __init__(
        self,
        manager: HttpAsyncSessionManager,
        max_connections: int,
        max_slots: int | None = None,
    ) -> None:
        self._manager: HttpAsyncSessionManager = manager
        self._max_connections: int = max_connections
        self._max_slots: int | None = max_slots
        self._slots: list[HttpSessionSlot[ClientSession]] = []  # TODO: implement using a min-heap
        self._lock: Lock = Lock()

    @property
    def has_capacity(self) -> bool:
        """
        Check if the pool can create a new session.

        Returns
        -------
        bool
            True if the number of slots is below `max_slots` or unlimited.
        """
        return self._max_slots is None or len(self._slots) < self._max_slots

    async def acquire(self) -> ClientSession:
        """
        Acquire a session from the pool asynchronously.

        Returns
        -------
        ClientSession
            An active aiohttp session object.

        Raises
        ------
        HttpSessionOverflowError
            If all sessions are full and the pool cannot create new slots.
        """
        async with self._lock:
            for slot in self._slots:
                if slot.ref_count < self._max_connections:
                    slot.ref_count += 1
                    return slot.session

            diagnostic_handler: DiagnosticHandler = DiagnosticHandler.get_or_create()
            diagnostic_handler.debug(msg="All HTTP sessions are full, creating a new one", logger=logger)

            if not self.has_capacity:
                diagnostic_handler.warn(
                    msg=(
                        f"HTTP sessions overflow: all slots are full. "
                        "Consider increasing the max number of allowed sessions"
                    ),
                    exception_cls=HttpSessionOverflowError,
                    exception_payload=self._max_slots,
                )

                # Fallback: reuse the least-used slot
                min_slot = min(self._slots, key=lambda s: s.ref_count)
                return min_slot.session

            new_session: ClientSession = await self._manager.get_or_create()
            new_slot: HttpSessionSlot[ClientSession] = HttpSessionSlot(new_session, ref_count=1)
            self._slots.append(new_slot)
            return new_session

    async def release(self, session: ClientSession) -> None:
        """
        Release a previously acquired session.

        Decrements the session's reference count. If it reaches 0,
        the session is closed and removed from the pool.

        Parameters
        ----------
        session : ClientSession
            The session to release.
        """
        async with self._lock:
            for slot in self._slots:
                if slot.session is session:
                    slot.ref_count -= 1
                    if slot.ref_count == 0:
                        await self._manager.reset()
                        self._slots.remove(slot)
                    return

    @asynccontextmanager
    async def session(self) -> AsyncIterator[ClientSession]:
        """
        Async context manager to safely acquire and release a session.

        Example
        -------
        >>> async with pool.session() as s:
        >>>     await s.get("https://example.com")

        Yields
        ------
        ClientSession
            An active aiohttp session object.
        """
        s = await self.acquire()
        try:
            yield s
        finally:
            await self.release(s)


class HttpAsyncSessionPoolThrottled(HttpAsyncSessionPool):
    """
    Async session pool with global concurrency limit using a semaphore.

    Extends `HttpAsyncSessionPool` by adding a semaphore to restrict the total
    number of concurrent coroutines across all sessions.
    """

    __slots__: tuple[str, ...] = ("_semaphore",)

    def __init__(
        self,
        manager: HttpAsyncSessionManager,
        max_connections: int,
        max_concurrency: int,
        max_slots: int | None = None,
    ) -> None:
        super().__init__(manager, max_connections, max_slots)
        self._semaphore: Semaphore = Semaphore(max_concurrency)

    async def acquire(self) -> ClientSession:
        """
        Acquire a session while respecting the global concurrency limit.

        Returns
        -------
        ClientSession
            An active aiohttp session object.

        Raises
        ------
        HttpSessionOverflowError
            If all sessions are full and max_slots is reached.
        """
        await self._semaphore.acquire()
        try:
            return await super().acquire()
        except Exception:
            self._semaphore.release()
            raise

    async def release(self, session: ClientSession) -> None:
        """
        Release a session and free a slot in the global semaphore.

        Parameters
        ----------
        session : ClientSession
            The session to release.
        """
        await super().release(session)
        self._semaphore.release()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[ClientSession]:
        """
        Async context manager for safe acquire/release with global concurrency control.

        Yields
        ------
        ClientSession
            An active aiohttp session object.
        """
        s = await self.acquire()
        try:
            yield s
        finally:
            await self.release(s)
