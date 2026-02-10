import pytest
from unittest.mock import AsyncMock
from aiohttp import ClientSession
import asyncio

from templisafe.diagnostic_handler import DiagnosticHandler
from templisafe.source.http.async_.http_async_session_pool import (
    HttpAsyncSessionPool,
    HttpAsyncSessionPoolThrottled,
    HttpSessionSlot,
)
from templisafe.exceptions.http_session_error import HttpSessionOverflowError
from templisafe.util import DiagnosticPolicy

# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def mock_manager():
    manager = AsyncMock()
    manager.get_or_create.side_effect = lambda: ClientSession()
    
    # Create future in the running loop
    async def reset():
        return None
    manager.reset.side_effect = reset

    return manager

@pytest.fixture(autouse=True)
def reset_diagnostic_handler_singleton():
    DiagnosticHandler._instance = None
    yield
    DiagnosticHandler._instance = None

# -------------------------
# Test acquire/release
# -------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pool_class", 
    [HttpAsyncSessionPool, HttpAsyncSessionPoolThrottled]
)
async def test_acquire_release_creates_and_releases_session(pool_class, mock_manager):
    pool = (
        pool_class(manager=mock_manager, max_connections=2, max_slots=2, max_concurrency=2)
        if pool_class is HttpAsyncSessionPoolThrottled
        else pool_class(manager=mock_manager, max_connections=2, max_slots=2)
    )

    # Initially empty
    assert len(pool._slots) == 0

    s1 = await pool.acquire()
    assert isinstance(s1, ClientSession)
    assert len(pool._slots) == 1
    assert pool._slots[0].ref_count == 1

    # Acquire same session, ref_count increases
    s2 = await pool.acquire()
    assert s1 is s2
    assert pool._slots[0].ref_count == 2

    # Release decreases ref_count
    await pool.release(s1)
    assert pool._slots[0].ref_count == 1

    await pool.release(s2)
    # Session removed after ref_count reaches 0
    assert len(pool._slots) == 0

# -------------------------
# Test max_slots overflow
# -------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pool_class",
    [HttpAsyncSessionPool, HttpAsyncSessionPoolThrottled]
)
async def test_max_slots_overflow_raises(pool_class, mock_manager):
    DiagnosticHandler.create(DiagnosticPolicy.STRICT)
    pool = (
        pool_class(manager=mock_manager, max_connections=1, max_slots=1, max_concurrency=2)
        if pool_class is HttpAsyncSessionPoolThrottled
        else pool_class(manager=mock_manager, max_connections=1, max_slots=1)
    )

    # Fill the pool
    s1 = await pool.acquire()
    # Attempt to create second session exceeding max_slots
    with pytest.raises(HttpSessionOverflowError):
        await pool.acquire()
    
    await pool.release(s1)

# -------------------------
# Test async context manager
# -------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pool_class",
    [HttpAsyncSessionPool, HttpAsyncSessionPoolThrottled]
)
async def test_context_manager_acquire_release(pool_class, mock_manager):
    pool = (
        pool_class(manager=mock_manager, max_connections=1, max_slots=2, max_concurrency=1)
        if pool_class is HttpAsyncSessionPoolThrottled
        else pool_class(manager=mock_manager, max_connections=1, max_slots=2)
    )

    async with pool.session() as s:
        assert isinstance(s, ClientSession)
        assert pool._slots[0].ref_count == 1
    # After context exit, ref_count should be 0
    assert len(pool._slots) == 0

# -------------------------
# Test HttpAsyncSessionPoolThrottled concurrency
# -------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("max_concurrency", [1, 2])
async def test_throttled_pool_limits_concurrency(mock_manager, max_concurrency):
    """
    Test that HttpAsyncSessionPoolThrottled limits the number of concurrent sessions
    according to the asyncio.Semaphore (max_concurrency).
    """
    DiagnosticHandler.create(DiagnosticPolicy.STRICT)

    pool = HttpAsyncSessionPoolThrottled(
        manager=mock_manager,
        max_connections=2,
        max_slots=10,
        max_concurrency=max_concurrency
    )

    active_sessions = 0
    active_sessions_lock = asyncio.Lock()
    sessions_recorded = []

    async def worker():
        nonlocal active_sessions
        async with pool.session() as s:
            assert isinstance(s, ClientSession)
            async with active_sessions_lock:
                active_sessions += 1
                current_active = active_sessions
            await asyncio.sleep(0.05)  # simulate work
            async with active_sessions_lock:
                active_sessions -= 1
            sessions_recorded.append(current_active)

    tasks = [asyncio.create_task(worker()) for _ in range(max_concurrency * 3)]
    await asyncio.gather(*tasks)

    # Check that the max number of concurrent sessions never exceeded the limit
    assert all(active <= max_concurrency for active in sessions_recorded)
    assert len(sessions_recorded) == max_concurrency * 3
