from dataclasses import dataclass
from overrides import overrides
import requests
import aiohttp

from templisafe.source.source import AsyncSource
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError, UninitializedSourceError

from .sync.http_sync_session_pool import SyncSessionPool
from .async_.http_async_session_pool import HttpAsyncSessionPool

##############################################################################################
# Http session pool
##############################################################################################

@dataclass(slots=True, frozen=True)
class HttpSessionPool:
    sync_pool: SyncSessionPool
    async_pool: HttpAsyncSessionPool

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

    __slots__: tuple[str, ...] = ("_session_pool", "_sync_session", "_async_session")

    def __init__(
            self, 
            settings: HttpSourceSettings,
            session_pool: HttpSessionPool
            ) -> None:
        super().__init__(settings)

        self._session_pool: HttpSessionPool = session_pool
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
        self._sync_session = self._session_pool.sync_pool.acquire()
        
    @overrides
    def close(self) -> None:
        if self._sync_session is not None:
            self._session_pool.sync_pool.release(self._sync_session)
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
        self._async_session = await self._session_pool.async_pool.acquire()

    @overrides
    async def aclose(self) -> None:
        if self._async_session is not None:
            await self._session_pool.async_pool.release(self._async_session)
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
