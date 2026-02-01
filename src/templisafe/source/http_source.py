from overrides import overrides
import requests
import aiohttp

from templisafe.source.source import AsyncSource
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError, UninitializedSourceError

##############################################################################################
# Sync Session Manager
##############################################################################################

class _HttpSyncSessionManager:
    """Singleton manager for shared synchronized HTTP sessions."""

    _session: requests.Session | None = None

    @classmethod
    def get_or_create(cls) -> requests.Session:
        """
        Retrieve the shared `requests.Session`, creating it if necessary.

        Returns
        -------
        requests.Session
            The singleton session instance.
        """
        if cls._session is None:
            cls._session = requests.Session()
        return cls._session

    @classmethod
    def reset(cls) -> None:
        """
        Close and remove the shared `requests.Session`.

        After calling this, the next `get_or_create()` call will create a new session. 
        Safe to call multiple times and on an already closed session.

        Returns
        -------
        None
        """
        if cls._session is not None:
            cls._session.close()    # safe to call on an already closed session
            cls._session = None    


##############################################################################################
# Async Session Manager
##############################################################################################

class _HttpAsyncSessionManager:
    """Singleton manager for shared asynchronous HTTP sessions."""

    _session: aiohttp.ClientSession | None = None

    @classmethod
    async def get_or_create(cls) -> aiohttp.ClientSession:
        """
        Retrieve the shared `aiohttp.ClientSession`, creating it if necessary.

        Returns
        -------
        aiohttp.ClientSession
            The singleton async session instance.
        """
        if cls._session is None:
            # Customize connector/limits here if needed for high concurrency
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def reset(cls) -> None:
        """
        Close and remove the shared `aiohttp.ClientSession`.

        After calling this, the next `get_or_create()` call will create a new session. 
        Safe to call multiple times and on an already closed session.

        Returns
        -------
        None
        """
        if cls._session is not None:
            if not cls._session.closed:
                await cls._session.close()
            cls._session = None


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

    __slots__: tuple[str, ...] = ("_sync_session", "_async_session")

    def __init__(self, settings: HttpSourceSettings) -> None:
        super().__init__(settings)
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
    # Synchronous read
    #-----------------------------
     
    @overrides
    def open(self) -> None:
        self._sync_session = _HttpSyncSessionManager.get_or_create()
        
    @overrides
    def close(self) -> None:
        _HttpSyncSessionManager.reset()
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
    # Asynchronous read
    #-----------------------------

    @overrides
    async def aopen(self) -> None:
        self._async_session = await _HttpAsyncSessionManager.get_or_create()

    @overrides
    async def aclose(self) -> None:
        await _HttpAsyncSessionManager.reset()
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
