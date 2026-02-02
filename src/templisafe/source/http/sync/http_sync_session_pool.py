from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock, Semaphore
from typing import Iterator
from overrides import overrides
from requests import Session

from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from .http_sync_session_manager import HttpSyncSessionManager
from ..http_session_slot import HttpSessionSlot

##############################################################################################
# Base Sync Session Pool
##############################################################################################

class SyncSessionPool:
    """
    Thread-safe pool of session objects with reference counting.

    This pool allows multiple consumers (sources) to share a limited number
    of HTTP sessions efficiently. Each session has a configurable maximum number
    of concurrent users (max_connections). When all sessions are fully used, 
    a new session is created automatically up to `max_slots`.
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
        manager: HttpSyncSessionManager, 
        max_connections: int,
        max_slots: int | None = None
    ) -> None:
        """
        Initialize the session pool.

        Args:
            manager (HttpSyncSessionManager): Session manager to create/reset sessions.
            max_connections (int): Maximum concurrent users per session.
            max_slots (int | None): Maximum number of sessions allowed. None = unlimited.
        """
        self._manager: HttpSyncSessionManager = manager
        self._slots: list[HttpSessionSlot[Session]] = []
        self._max_connections: int = max_connections
        self._max_slots: int | None = max_slots
        self._lock: Lock = Lock()

    @property
    def has_capacity(self) -> bool:
        return self._max_slots is None or len(self._slots) < self._max_slots

    def acquire(self) -> Session:
        """
        Acquire a session from the pool.

        Finds a session with available capacity (ref_count < max_connections),
        or creates a new session if all are full and max_slots allows.

        Raises:
            HttpSessionOverflowError: If the pool has reached max_slots.

        Returns:
            session: The acquired HTTP session.
        """
        with self._lock:
            # Find a session with available capacity
            for slot in self._slots:
                if slot.ref_count < self._max_connections:
                    slot.ref_count += 1
                    return slot.session

            # All sessions full; create a new one if allowed
            if not self.has_capacity:
                raise HttpSessionOverflowError(self._max_slots)

            new_session = self._manager.get_or_create()
            slot = HttpSessionSlot[Session](new_session, ref_count=1)
            self._slots.append(slot)
            return new_session

    def release(self, session: Session) -> None:
        """
        Release a previously acquired session.

        Decrements the reference count for the session. If the ref_count reaches 0,
        the session is closed and removed from the pool.

        Args:
            session (session): The session to release.
        """
        with self._lock:
            for slot in self._slots:
                if slot.session is session:
                    slot.ref_count -= 1
                    if slot.ref_count == 0:
                        self._manager.reset()
                        self._slots.remove(slot)
                    return

    @contextmanager
    def session(self) -> Iterator[Session]:
        """
        Context manager to acquire and release a session safely.

        Usage:
            with pool.session() as session:
                response = session.get(url)

        Yields:
            session: The acquired session.
        """
        session = self.acquire()
        try:
            yield session
        finally:
            self.release(session)

##############################################################################################
# Sync Session Pool with Global Concurrency Limit
##############################################################################################

class SyncSessionPoolLimited(SyncSessionPool):
    """
    Thread-safe session pool with a global concurrency limit.

    Extends SyncSessionPool to add a Semaphore limiting the total number
    of concurrent requests across all sessions in the pool.
    """

    __slots__ = ("_semaphore",)

    def __init__(
        self, 
        manager: HttpSyncSessionManager, 
        max_connections: int,
        max_concurrency: int,
        max_slots: int | None = None
    ) -> None:
        """
        Initialize the limited session pool.

        Args:
            manager (HttpSyncSessionManager): Session manager.
            max_connections (int): Max users per session.
            max_concurrency (int): Max concurrent requests across the pool.
            max_slots (int | None): Max number of sessions allowed in the pool.
        """
        super().__init__(manager, max_connections, max_slots)
        self._semaphore: Semaphore = Semaphore(max_concurrency)

    @overrides
    def acquire(self) -> Session:
        """
        Acquire a session while respecting the global concurrency limit.

        Blocks if the global limit is reached.

        Returns:
            session: Acquired session.

        Raises:
            Exception: Any exception during session creation will release the semaphore.
        """
        self._semaphore.acquire()
        try:
            return super().acquire()
        except Exception:
            self._semaphore.release()
            raise

    @overrides
    def release(self, session: Session) -> None:
        """
        Release a session and free a slot in the global semaphore.

        Args:
            session (session): Session to release.
        """
        super().release(session)
        self._semaphore.release()

    @contextmanager
    def session(self) -> Iterator[Session]:
        """
        Context manager for safe acquire/release with global concurrency control.

        Usage:
            with pool.session() as session:
                response = session.get(url)

        Yields:
            session: The acquired session.
        """
        session = self.acquire()
        try:
            yield session
        finally:
            self.release(session)
