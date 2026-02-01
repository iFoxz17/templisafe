import requests
import aiohttp

from templisafe.settings.source.http.http_session_settings import (
    HttpSyncSessionSettings,
    HttpAsyncSessionSettings
)

##############################################################################################
# Sync Session Manager
##############################################################################################

class HttpSyncSessionManager:
    """Singleton manager for synchronized HTTP sessions."""

    __slots__: tuple[str, ...] = ("_settings", "_session")

    def __init__(
        self,
        settings: HttpSyncSessionSettings,
        session: requests.Session | None = None,
    ) -> None:
        self._settings: HttpSyncSessionSettings = settings
        self._session: requests.Session | None = session

    def get_or_create(self) -> requests.Session:
        """
        Retrieve the `requests.Session`, creating it if necessary.
        """
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def reset(self) -> None:
        """
        Close and remove the `requests.Session`.
        """
        if self._session is not None:
            self._session.close()
            self._session = None


##############################################################################################
# Async Session Manager
##############################################################################################

class HttpAsyncSessionManager:
    """Singleton manager for asynchronous HTTP sessions."""

    __slots__: tuple[str, ...] = ("_settings", "_session")

    def __init__(
        self,
        settings: HttpAsyncSessionSettings,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._settings: HttpAsyncSessionSettings = settings
        self._session: aiohttp.ClientSession | None = session

    async def get_or_create(self) -> aiohttp.ClientSession:
        """Retrieve the `aiohttp.ClientSession`, creating it if necessary."""
        
        if self._session is None:
            connector = aiohttp.TCPConnector(
                limit=self._settings.max_connections,
                limit_per_host=self._settings.max_connections_per_host,
                force_close=self._settings.force_close,
                ttl_dns_cache=self._settings.ttl_dns_cache,
            )

            self._session = aiohttp.ClientSession(
                connector=connector,
            )

        return self._session

    async def reset(self) -> None:
        """
        Close and remove the `aiohttp.ClientSession`.
        """
        if self._session is not None:
            if not self._session.closed:
                await self._session.close()
            self._session = None

##############################################################################################
# Session Manager Facade
##############################################################################################

class HttpSessionManager:

    __slots__: tuple[str, ...] = ("_sync_manager", "_async_manager")

    def __init__(
            self, 
            sync_manager: HttpSyncSessionManager,
            async_manager: HttpAsyncSessionManager,
            ) -> None:
        self._sync_manager: HttpSyncSessionManager = sync_manager
        self._async_manager: HttpAsyncSessionManager = async_manager
    
    def get_or_create_sync(self) -> requests.Session:
        return self._sync_manager.get_or_create()
    
    def reset_sync(self) -> None:
        self._sync_manager.reset()

    async def get_or_create_async(self) -> aiohttp.ClientSession:
        return await self._async_manager.get_or_create()
    
    async def reset_async(self) -> None:
        await self._async_manager.reset()

