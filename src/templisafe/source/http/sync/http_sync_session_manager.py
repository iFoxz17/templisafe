from requests import Session
from requests.adapters import HTTPAdapter

from templisafe.settings.source.http.http_session_settings import (
    HttpSyncSessionSettings,
)

##############################################################################################
# Factory
##############################################################################################


class HttpSyncSessionFactory:
    """
    Factory for creating `requests.Session` objects with a configured
    HTTPAdapter for connection pooling.
    """

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self) -> None:
        pass

    def create(self, settings: HttpSyncSessionSettings) -> Session:
        """
        Create a new `requests.Session` object configured with connection pooling.

        Parameters
        ----------
        settings : HttpSyncSessionSettings
            Http synchronized session settings.

        Returns
        -------
        Session
            A configured requests session ready for use.
        """
        session: Session = Session()
        adapter: HTTPAdapter = HTTPAdapter(
            pool_connections=settings.pool_connections,
            pool_maxsize=settings.pool_maxsize,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session


##############################################################################################
# Manager
##############################################################################################


class HttpSyncSessionManager:
    """
    Manager and owner of a single `requests.Session`.

    Provides controlled access to a session instance and allows resetting
    it when needed. Ensures that only one session exists at a time.
    """

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_session")

    def __init__(
        self,
        settings: HttpSyncSessionSettings,
        factory: HttpSyncSessionFactory | None = None,
    ) -> None:
        self._settings: HttpSyncSessionSettings = settings
        self._factory: HttpSyncSessionFactory = factory or HttpSyncSessionFactory()
        self._session: Session | None = None

    def get_or_create(self) -> Session:
        """
        Get the existing session or create a new one if it doesn't exist.

        Returns
        -------
        Session
            The managed `requests.Session` object.
        """
        if self._session is None:
            self._session = self._factory.create(self._settings)
        return self._session

    def reset(self) -> None:
        """
        Close and reset the managed session.

        After this call, `get_or_create` will create a new session.
        """
        if self._session is not None:
            self._session.close()
            self._session = None
