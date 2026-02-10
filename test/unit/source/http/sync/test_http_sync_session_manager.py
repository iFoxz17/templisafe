import pytest
from requests import Session
from requests.adapters import HTTPAdapter

from templisafe.settings.source.http.http_session_settings import HttpSyncSessionSettings
from templisafe.source.http.sync.http_sync_session_manager import HttpSyncSessionFactory, HttpSyncSessionManager

@pytest.fixture
def settings() -> HttpSyncSessionSettings:
    return HttpSyncSessionSettings(
        pool_connections=5,
        pool_maxsize=10
    )

def test_factory_creates_session(settings):
    factory = HttpSyncSessionFactory()
    session = factory.create(settings)

    assert isinstance(session, Session)
    # Check that HTTPAdapter is mounted
    assert isinstance(session.adapters["http://"], HTTPAdapter)
    assert isinstance(session.adapters["https://"], HTTPAdapter)
    
def test_manager_get_or_create_creates_session(settings):
    manager = HttpSyncSessionManager(settings)
    session1 = manager.get_or_create()
    session2 = manager.get_or_create()

    assert session1 is session2  # Always returns the same session
    assert isinstance(session1, Session)

def test_manager_reset(settings):
    manager = HttpSyncSessionManager(settings)
    session1 = manager.get_or_create()
    manager.reset()
    session2 = manager.get_or_create()

    assert session1 is not session2  # After reset, new session is created
    assert isinstance(session2, Session)

def test_manager_reset_without_session(settings):
    manager = HttpSyncSessionManager(settings)
    # Should not raise an exception
    manager.reset()
