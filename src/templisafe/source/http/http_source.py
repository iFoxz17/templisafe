from overrides import overrides
import requests
import aiohttp

from templisafe.source.source import AsyncSource
from templisafe.source.http.http_session_manager import HttpSessionManager
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError, UninitializedSourceError

##############################################################################################
# Http source
##############################################################################################

class HttpSource(AsyncSource):
    """
    HTTP source using shared sessions. 
    Implements both synchronous and asynchronous reads:
        - Synchronous reads use a shared `requests.Session`.  
        - Asynchronous reads use a shared `aiohttp.ClientSession`.  
    """

    __slots__: tuple[str, ...] = ("_session_manager", "_sync_session", "_async_session")

    def __init__(
            self, 
            settings: HttpSourceSettings,
            session_manager: HttpSessionManager
            ) -> None:
        super().__init__(settings)

        self._session_manager: HttpSessionManager = session_manager
        self._sync_session: requests.Session | None = None
        self._async_session: aiohttp.ClientSession | None = None

    @property
    def settings(self) -> HttpSourceSettings:
        assert isinstance(self._settings, HttpSourceSettings)
        return self._settings

    @property
    def url(self) -> str:
        return self.settings.url
    
    #-----------------------------
    # Synchronous flow
    #-----------------------------
     
    @overrides
    def open(self) -> None:
        self._sync_session = self._session_manager.get_or_create_sync()
        
    @overrides
    def close(self) -> None:
        self._session_manager.reset_sync()
        self._sync_session = None

    @overrides
    def read(self) -> str:
        session: requests.Session | None = self._sync_session
        if session is None:
            raise UninitializedSourceError()
        
        try:
            response: requests.Response = session.get(self.url, timeout=self.settings.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise HttpSourceError(self.url) from e

    #-----------------------------
    # Asynchronous flow
    #-----------------------------

    @overrides
    async def aopen(self) -> None:
        self._async_session = await self._session_manager.get_or_create_async()

    @overrides
    async def aclose(self) -> None:
        await self._session_manager.reset_async()
        self._async_session = None
        
    @overrides
    async def aread(self) -> str:
        session: aiohttp.ClientSession | None = self._async_session
        if session is None:
            raise UninitializedSourceError()
        
        try:
            timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=self.settings.timeout)
            async with session.get(self.url, timeout=timeout) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            raise HttpSourceError(self.url) from e
