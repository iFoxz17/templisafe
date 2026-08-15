import logging
from contextlib import contextmanager
from threading import Lock, Semaphore
from typing import Iterator

from requests import Session

from templisafe.core.diagnostic_handler import DiagnosticHandler
from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from templisafe.source.http.sync.http_sync_session_manager import HttpSyncSessionManager

from ..http_session_slot import HttpSessionSlot

logger: logging.Logger = logging.getLogger(__name__)


class HttpSyncSessionPool:
    """
    Thread-safe pool of `requests.Session` objects with reference counting.

    This pool allows multiple consumers to share a limited number of HTTP sessions
    efficiently. Each session has a configurable maximum number of concurrent users
    (`max_connections`). New sessions are created automatically up to `max_slots`
    if all existing sessions are fully used. If no more sessions can be created, the
    behaviour depends on the set diagnostic policy.
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
        max_slots: int | None = None,
    ) -> None:
        self._manager: HttpSyncSessionManager = manager
        self._max_connections: int = max_connections
        self._max_slots: int | None = max_slots
        self._slots: list[HttpSessionSlot[Session]] = []  # TODO: implement using a min-heap
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

    def acquire(self) -> Session:
        """
        Acquire a session from the pool.

        Returns
        -------
        Session
            An active session object ready for use.

        Raises
        ------
        HttpSessionOverflowError
            If all sessions are full and the pool cannot create new slots.
        """
        with self._lock:
            for slot in self._slots:
                if slot.ref_count < self._max_connections:
                    slot.ref_count += 1
                    return slot.session

            diagnostic_handler: DiagnosticHandler = DiagnosticHandler.get_or_create()
            diagnostic_handler.debug(
                msg="All HTTP sessions are full, creating a new one",
                logger=logger,
            )

            if not self.has_capacity:
                diagnostic_handler.warn(
                    msg=(
                        f"HTTP sessions overflow: all slots are full. "
                        "Consider increasing the max number of sessions allowed"
                    ),
                    exception_cls=HttpSessionOverflowError,
                    exception_payload=self._max_slots,
                )

                # Fallback: reuse the least-used slot
                min_slot = min(self._slots, key=lambda s: s.ref_count)
                return min_slot.session

            # Create a new session
            new_session: Session = self._manager.get_or_create()
            new_slot = HttpSessionSlot(new_session, ref_count=1)
            self._slots.append(new_slot)
            return new_session

    def release(self, session: Session) -> None:
        """
        Release a previously acquired session.

        Decrements the session's reference count. If it reaches 0,
        the session is closed and removed from the pool.

        Parameters
        ----------
        session : Session
            The session to release.
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
        Context manager to safely acquire and release a session.

        Example
        -------
        >>> with pool.session() as s:
        >>>     s.get("https://example.com")

        Yields
        ------
        Session
            An active session object.
        """
        s: Session = self.acquire()
        try:
            yield s
        finally:
            self.release(s)


class HttpSyncSessionPoolThrottled(HttpSyncSessionPool):
    """
    Thread-safe pool of `requests.Session` objects with global concurrency limit.

    Extends `HttpSyncSessionPool` by adding a `Semaphore` to restrict the total
    number of concurrent requests across all sessions.
    """

    __slots__: tuple[str, ...] = ("_semaphore",)

    def __init__(
        self,
        manager: HttpSyncSessionManager,
        max_connections: int,
        max_concurrency: int,
        max_slots: int | None = None,
    ) -> None:
        super().__init__(manager, max_connections, max_slots)
        self._semaphore: Semaphore = Semaphore(max_concurrency)

    def acquire(self) -> Session:
        """
        Acquire a session while respecting the global concurrency limit.

        Returns
        -------
        Session
            An active session object.

        Raises
        ------
        HttpSessionOverflowError
            If all sessions are full and max_slots is reached.
        """
        self._semaphore.acquire()
        try:
            return super().acquire()
        except Exception:
            self._semaphore.release()
            raise

    def release(self, session: Session) -> None:
        """
        Release a session and free a slot in the global semaphore.

        Parameters
        ----------
        session : Session
            The session to release.
        """
        super().release(session)
        self._semaphore.release()

    @contextmanager
    def session(self) -> Iterator[Session]:
        """
        Context manager for safe acquire/release with global concurrency control.

        Yields
        ------
        Session
            An active session object.
        """
        s: Session = self.acquire()
        try:
            yield s
        finally:
            self.release(s)
