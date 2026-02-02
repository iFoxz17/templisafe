import requests
from requests.adapters import HTTPAdapter

from templisafe.settings.source.http.http_sync_session_settings import HttpSyncSessionSettings

##############################################################################################
# Factory
##############################################################################################

class HttpSyncSessionFactory:
    """Factory of `requests.Session` objects."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self) -> None:
        pass

    def create(self, settings: HttpSyncSessionSettings) -> requests.Session:
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=settings.pool_connections,
            pool_maxsize=settings.pool_maxsize
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

##############################################################################################
# Manager
##############################################################################################

class HttpSyncSessionManager:
    """Manager and owner of a single `requests.Session`."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_session")

    def __init__(
            self, 
            settings: HttpSyncSessionSettings,
            factory: HttpSyncSessionFactory | None = None
            ) -> None:
        self._settings: HttpSyncSessionSettings = settings
        self._factory: HttpSyncSessionFactory = factory or HttpSyncSessionFactory()
        self._session: requests.Session | None = None

    def get_or_create(self) -> requests.Session:
        if self._session is None:
            self._session = self._factory.create(self._settings)
        return self._session

    def reset(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None