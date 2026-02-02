import warnings
from contextlib import contextmanager
from threading import Lock, Semaphore
from typing import Iterator
from requests import Session

from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from templisafe.source.http.sync.http_sync_session_manager import HttpSyncSessionManager
from ..http_session_slot import HttpSessionSlot

class HttpSyncSessionPool:
    """Thread-safe pool of requests.Session objects with reference counting."""

    __slots__: tuple[str, ...] = ("_manager", "_slots", "_max_connections", "_max_slots", "_lock")

    def __init__(
            self, 
            manager: HttpSyncSessionManager, 
            max_connections: int, 
            max_slots: int | None = None
            ) -> None:
        self._manager: HttpSyncSessionManager = manager
        self._max_connections: int = max_connections
        self._max_slots: int | None = max_slots
        self._slots: list[HttpSessionSlot[Session]] = []
        self._lock: Lock = Lock()

    @property
    def has_capacity(self) -> bool:
        return self._max_slots is None or len(self._slots) < self._max_slots

    def acquire(self) -> Session:
        with self._lock:
            for slot in self._slots:
                if slot.ref_count < self._max_connections:
                    slot.ref_count += 1
                    return slot.session

            #TODO: avoid raising in production mode
            if not self.has_capacity:
                warnings.warn(f"HTTP sessions overflow: max sessions {self._max_slots}")
                raise HttpSessionOverflowError(self._max_slots)

            new_session: Session = self._manager.get_or_create()
            slot: HttpSessionSlot[Session] = HttpSessionSlot(new_session, ref_count=1)
            self._slots.append(slot)
            return new_session

    def release(self, session: Session) -> None:
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
        s: Session = self.acquire()
        try:
            yield s
        finally:
            self.release(s)


class HttpSyncSessionPoolThrottled(HttpSyncSessionPool):
    """Sync session pool with a global concurrency limit (Semaphore)."""

    __slots__: tuple[str, ...] = ("_semaphore",)

    def __init__(
            self, 
            manager: HttpSyncSessionManager, 
            max_connections: int, 
            max_concurrency: int, 
            max_slots: int | None = None
            ) -> None:
        super().__init__(manager, max_connections, max_slots)
        self._semaphore: Semaphore = Semaphore(max_concurrency)

    def acquire(self) -> Session:
        self._semaphore.acquire()
        try:
            return super().acquire()
        except Exception:
            self._semaphore.release()
            raise

    def release(self, session: Session) -> None:
        super().release(session)
        self._semaphore.release()

    @contextmanager
    def session(self) -> Iterator[Session]:
        s: Session = self.acquire()
        try:
            yield s
        finally:
            self.release(s)