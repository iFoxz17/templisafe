from overrides import overrides
import asyncio
import aiohttp

from templisafe.source.source import AsyncSource
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError

# Module-level shared session (lazy-initialized, auto-managed)
_http_session: aiohttp.ClientSession | None = None
_session_lock = asyncio.Lock()

async def _get_http_session() -> aiohttp.ClientSession:
    """Get or create the shared HTTP session for all HttpSource instances."""
    global _http_session
    
    async with _session_lock:
        if _http_session is None or _http_session.closed:
            connector = aiohttp.TCPConnector(
                limit=0,             # No total connection limit
                limit_per_host=100,  # Max 100 concurrent per host
                ttl_dns_cache=300,   # Cache DNS for 5 minutes
            )
            timeout = aiohttp.ClientTimeout(total=30)
            _http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
            )
    
    return _http_session

async def _reset_http_session() -> None:
    """Reset the shared session. Used primarily for testing."""
    global _http_session
    
    async with _session_lock:
        if _http_session and not _http_session.closed:
            await _http_session.close()
        _http_session = None

class HttpSource(AsyncSource):
    """
    A source implementation that retrieves content from an HTTP URL.
    
    All HttpSource instances automatically share a single aiohttp.ClientSession
    for efficiency when handling thousands of concurrent async requests.
    
    The synchronous read() method uses the requests library for simplicity.
    """

    def __init__(self, settings: HttpSourceSettings) -> None:
        super().__init__(settings)

    @property
    def url(self) -> str:
        assert isinstance(self._settings, HttpSourceSettings)
        return self._settings.url
    
    @overrides
    def read(self) -> str:
        import requests
        try:
            response = requests.get(self.url, timeout=30)
            if response.status_code != 200:
                raise HttpSourceError(self.url, status_code=response.status_code)
            return response.text
        except requests.RequestException as e:
            raise HttpSourceError(self.url) from e

    async def _fetch(self) -> str:
        """Core async fetch logic using shared aiohttp session."""
        try:
            session = await _get_http_session()
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise HttpSourceError(self.url, status_code=response.status)
                return await response.text()
        except aiohttp.ClientError as e:
            raise HttpSourceError(self.url) from e

    @overrides
    async def aread(self) -> str:
        """Asynchronous read using shared aiohttp session."""
        return await self._fetch()