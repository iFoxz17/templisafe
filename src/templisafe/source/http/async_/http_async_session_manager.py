from aiohttp import ClientSession, TCPConnector

from templisafe.settings.source.http.http_session_settings import HttpAsyncSessionSettings

##############################################################################################
# Factory
##############################################################################################

class HttpAsyncSessionFactory:
    """Factory of `requests.Session` objects."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self) -> None:
        pass

    def create(self, settings: HttpAsyncSessionSettings) -> ClientSession:
        connector: TCPConnector = TCPConnector(
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
    """Manager and owner of a single `requests.Session`."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_session")

    def __init__(
            self, 
            settings: HttpAsyncSessionSettings,
            factory: HttpAsyncSessionFactory | None = None
            ) -> None:
        self._settings: HttpAsyncSessionSettings = settings
        self._factory: HttpAsyncSessionFactory = factory or HttpAsyncSessionFactory()
        self._session: ClientSession | None = None

    async def get_or_create(self) -> ClientSession:
        if self._session is None:
            self._session = self._factory.create(self._settings)
        return self._session

    async def reset(self) -> None:
        if self._session is not None:
            if not self._session.closed:
                await self._session.close()
            self._session = None
