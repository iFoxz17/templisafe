from aiohttp import ClientSession, TCPConnector
from templisafe.settings.source.http.http_session_settings import HttpAsyncSessionSettings

##############################################################################################
# Factory
##############################################################################################

class HttpAsyncSessionFactory:
    """
    Factory for creating `aiohttp.ClientSession` objects with a configured TCPConnector.
    """

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self) -> None:
        pass

    def create(self, settings: HttpAsyncSessionSettings) -> ClientSession:
        """
        Create a new `aiohttp.ClientSession` with a TCPConnector configured
        according to the provided settings.

        Parameters
        ----------
        settings : HttpAsyncSessionSettings
            Http asynchronized session settings.

        Returns
        -------
        ClientSession
            A configured aiohttp session ready for async usage.
        """
        connector = TCPConnector(
            limit=settings.max_connections,
            limit_per_host=settings.max_connections_per_host,
            force_close=settings.force_close,
            ttl_dns_cache=settings.ttl_dns_cache,
        )
        return ClientSession(connector=connector)

##############################################################################################
# Manager
##############################################################################################

class HttpAsyncSessionManager:
    """
    Manager and owner of a single `aiohttp.ClientSession`.

    Provides controlled async access to a single session instance
    and allows resetting (closing) it when needed.
    """

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_session")

    def __init__(
        self,
        settings: HttpAsyncSessionSettings,
        factory: HttpAsyncSessionFactory | None = None
    ) -> None:
        """
        Initialize the async session manager.

        Parameters
        ----------
        settings : HttpAsyncSessionSettings
            Settings used to configure the async session.
        factory : HttpAsyncSessionFactory | None
            Optional factory for creating sessions. If None, a default factory is used.
        """
        self._settings: HttpAsyncSessionSettings = settings
        self._factory: HttpAsyncSessionFactory = factory or HttpAsyncSessionFactory()
        self._session: ClientSession | None = None

    async def get_or_create(self) -> ClientSession:
        """
        Get the existing session or create a new one if it doesn't exist.

        Returns
        -------
        ClientSession
            The managed `aiohttp.ClientSession`.
        """
        if self._session is None:
            self._session = self._factory.create(self._settings)
        return self._session

    async def reset(self) -> None:
        """
        Close and reset the managed session.

        After this call, `get_or_create` will create a new session.
        """
        if self._session is not None:
            if not self._session.closed:
                await self._session.close()
            self._session = None
