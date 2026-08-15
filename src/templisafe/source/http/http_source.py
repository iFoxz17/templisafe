import asyncio
from dataclasses import dataclass
from typing import ClassVar

from aiohttp import ClientError, ClientSession, ClientTimeout
from overrides import overrides
from requests import RequestException, Response, Session

from templisafe.exceptions.source_error import HttpSourceError, UninitializedSourceError
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.source.source import AsyncSource

from .async_.http_async_session_pool import HttpAsyncSessionPool
from .sync.http_sync_session_pool import HttpSyncSessionPool

##############################################################################################
# Http session pool
##############################################################################################


@dataclass(slots=True, frozen=True)
class HttpSessionPool:
    sync_pool: HttpSyncSessionPool
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
    _DEFAULT_POOLS: ClassVar[dict[tuple[object, object, int | None], HttpSessionPool]] = {}

    def __init__(self, settings: HttpSourceSettings, session_pool: HttpSessionPool | None = None) -> None:
        super().__init__(settings)

        self._session_pool: HttpSessionPool = session_pool or self._get_default_pool(settings)
        self._sync_session: Session | None = None
        self._async_session: ClientSession | None = None

    def _get_default_pool(self, settings: HttpSourceSettings) -> HttpSessionPool:
        try:
            loop_id: int | None = id(asyncio.get_running_loop())
        except RuntimeError:
            loop_id = None
        key = (settings.sync_session_settings, settings.async_session_settings, loop_id)
        if key not in self._DEFAULT_POOLS:
            self._DEFAULT_POOLS[key] = self._create_default_pool(settings)
        return self._DEFAULT_POOLS[key]

    def _create_default_pool(self, settings: HttpSourceSettings) -> HttpSessionPool:
        from .async_.http_async_session_manager import HttpAsyncSessionManager
        from .http_source_factory import HttpSourceFactory
        from .sync.http_sync_session_manager import HttpSyncSessionManager

        factory = HttpSourceFactory()
        sync_manager = HttpSyncSessionManager(settings.sync_session_settings)
        async_manager = HttpAsyncSessionManager(settings.async_session_settings)
        return HttpSessionPool(
            sync_pool=factory._create_sync_pool(
                sync_manager,
                settings.sync_session_settings,
            ),
            async_pool=factory._create_async_pool(
                async_manager,
                settings.async_session_settings,
            ),
        )

    @property
    def settings(self) -> HttpSourceSettings:
        assert isinstance(self._settings, HttpSourceSettings)
        return self._settings

    @property
    def url(self) -> str:
        return self.settings.url

    # -----------------------------
    # Synchronous flow
    # -----------------------------

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
        session: Session | None = self._sync_session
        if session is None:
            raise UninitializedSourceError()

        try:
            response: Response = session.get(self.url, timeout=self.settings.timeout)
            response.raise_for_status()
            return response.text
        except RequestException as e:
            raise HttpSourceError(self.url) from e

    # -----------------------------
    # Asynchronous flow
    # -----------------------------

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
        session: ClientSession | None = self._async_session
        if session is None:
            raise UninitializedSourceError()

        try:
            timeout: ClientTimeout = ClientTimeout(total=self.settings.timeout)
            async with session.get(self.url, timeout=timeout) as response:
                response.raise_for_status()
                return await response.text()
        except ClientError as e:
            raise HttpSourceError(self.url) from e
