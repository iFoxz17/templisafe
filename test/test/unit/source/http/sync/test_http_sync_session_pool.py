import threading
import time
from unittest.mock import Mock

import pytest
from requests import Session

from templisafe.core.diagnostic_handler import DiagnosticHandler
from templisafe.core.util import DiagnosticPolicy
from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from templisafe.source.http.sync.http_sync_session_pool import (
    HttpSessionSlot,
    HttpSyncSessionPool,
    HttpSyncSessionPoolThrottled,
)


@pytest.fixture
def mock_manager():
    manager = Mock()
    manager.get_or_create.side_effect = lambda: Session()
    manager.reset.return_value = None
    return manager


@pytest.fixture(autouse=True)
def reset_diagnostic_handler_singleton():
    # Reset singleton between tests
    DiagnosticHandler._instance = None
    yield
    DiagnosticHandler._instance = None


# -------------------------
# Test acquire/release
# -------------------------


@pytest.mark.parametrize("pool_class", [HttpSyncSessionPool, HttpSyncSessionPoolThrottled])
def test_acquire_release_creates_and_releases_session(pool_class, mock_manager):
    pool = (
        pool_class(manager=mock_manager, max_connections=2, max_slots=2, max_concurrency=2)
        if pool_class is HttpSyncSessionPoolThrottled
        else pool_class(manager=mock_manager, max_connections=2, max_slots=2)
    )

    # Initially empty
    assert len(pool._slots) == 0

    s1 = pool.acquire()
    assert isinstance(s1, Session)
    assert len(pool._slots) == 1
    assert pool._slots[0].ref_count == 1

    # Acquire same session, ref_count increases
    s2 = pool.acquire()
    assert s1 is s2
    assert pool._slots[0].ref_count == 2

    # Release decreases ref_count
    pool.release(s1)
    assert pool._slots[0].ref_count == 1

    pool.release(s2)
    # Session removed after ref_count reaches 0
    assert len(pool._slots) == 0


# -------------------------
# Test max_slots overflow
# -------------------------


@pytest.mark.parametrize("pool_class", [HttpSyncSessionPool, HttpSyncSessionPoolThrottled])
def test_max_slots_overflow_raises(pool_class, mock_manager):
    DiagnosticHandler.create(DiagnosticPolicy.STRICT)
    pool = (
        pool_class(manager=mock_manager, max_connections=1, max_slots=1, max_concurrency=2)
        if pool_class is HttpSyncSessionPoolThrottled
        else pool_class(manager=mock_manager, max_connections=1, max_slots=1)
    )

    # Fill the pool
    s1 = pool.acquire()
    # Attempt to create second session exceeding max_slots
    with pytest.raises(HttpSessionOverflowError):
        pool.acquire()

    pool.release(s1)


# -------------------------
# Test context manager
# -------------------------


@pytest.mark.parametrize("pool_class", [HttpSyncSessionPool, HttpSyncSessionPoolThrottled])
def test_context_manager_acquire_release(pool_class, mock_manager):
    pool = (
        pool_class(manager=mock_manager, max_connections=1, max_slots=2, max_concurrency=1)
        if pool_class is HttpSyncSessionPoolThrottled
        else pool_class(manager=mock_manager, max_connections=1, max_slots=2)
    )

    with pool.session() as s:
        assert isinstance(s, Session)
        assert pool._slots[0].ref_count == 1
    # After context exit, ref_count should be 0
    assert len(pool._slots) == 0


# -------------------------
# Test HttpSyncSessionPoolThrottled concurrency
# -------------------------


@pytest.mark.parametrize("max_concurrency", [1, 2])
def test_throttled_pool_limits_concurrency(mock_manager, max_concurrency):
    """
    Test that HttpSyncSessionPoolThrottled limits the number of concurrent sessions
    according to the Semaphore (max_concurrency).
    """
    DiagnosticHandler.create(DiagnosticPolicy.STRICT)

    pool = HttpSyncSessionPoolThrottled(
        manager=mock_manager,
        max_connections=2,
        max_slots=10,
        max_concurrency=max_concurrency,
    )

    active_sessions = 0
    lock = threading.Lock()
    threads_done = []

    def worker():
        nonlocal active_sessions
        with pool.session() as s:
            assert isinstance(s, Session)
            with lock:
                active_sessions += 1
                current_active = active_sessions
            # Simulate some work
            time.sleep(0.1)
            with lock:
                active_sessions -= 1
            threads_done.append(current_active)

    threads = [threading.Thread(target=worker) for _ in range(max_concurrency * 3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Check that the max number of concurrent sessions never exceeded the limit
    assert all(active <= max_concurrency for active in threads_done)
    # Ensure all threads ran
    assert len(threads_done) == max_concurrency * 3
