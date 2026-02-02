from templisafe.settings.source.http.http_session_settings import HttpSyncSessionSettings, HttpAsyncSessionSettings
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings

from .http_source import HttpSource, HttpSessionPool
from .sync.http_sync_session_pool import HttpSyncSessionPool, HttpSyncSessionPoolThrottled
from .sync.http_sync_session_manager import HttpSyncSessionManager
from .async_.http_async_session_pool import HttpAsyncSessionPool, HttpAsyncSessionPoolThrottled
from .async_.http_async_session_manager import HttpAsyncSessionManager

class HttpSourceFactory:
    """Creates `HttpSource` instances from http source settings."""

    def _create_sync_pool(
            self, 
            manager: HttpSyncSessionManager,
            sync_settings: HttpSyncSessionSettings
            ) -> HttpSyncSessionPool:
        
        max_connections: int = sync_settings.pool_connections * sync_settings.pool_maxsize
        if sync_settings.max_concurrency is not None:
            return HttpSyncSessionPoolThrottled(
                manager=manager,
                max_connections=max_connections,
                max_concurrency=sync_settings.max_concurrency,
                max_slots=sync_settings.max_slots
            )
        
        return HttpSyncSessionPool(
                manager=manager,
                max_connections=max_connections,
                max_slots=sync_settings.max_slots
            )
    
    def _create_async_pool(
            self, 
            manager: HttpAsyncSessionManager,
            async_settings: HttpAsyncSessionSettings
            ) -> HttpAsyncSessionPool:
        
        max_connections: int = min(
            async_settings.max_connections,
            async_settings.max_connections_per_host
            ) 
        
        if async_settings.max_concurrency is not None:
            return HttpAsyncSessionPoolThrottled(
                manager=manager,
                max_connections=max_connections,
                max_concurrency=async_settings.max_concurrency,
                max_slots=async_settings.max_slots
            )
        
        return HttpAsyncSessionPool(
                manager=manager,
                max_connections=async_settings.max_connections,
                max_slots=async_settings.max_slots
            )
        
    def create(self, settings: HttpSourceSettings) -> HttpSource:
        """Create a `HttpSource` instance for the given settings."""

        sync_settings: HttpSyncSessionSettings = settings.sync_session_settings
        async_settings: HttpAsyncSessionSettings = settings.async_session_settings

        sync_manager: HttpSyncSessionManager = HttpSyncSessionManager(sync_settings) 
        async_manager: HttpAsyncSessionManager = HttpAsyncSessionManager(async_settings)

        sync_pool: HttpSyncSessionPool = self._create_sync_pool(
            sync_manager, sync_settings
        )
        async_pool: HttpAsyncSessionPool = self._create_async_pool(
            async_manager, async_settings
        )

        pool: HttpSessionPool = HttpSessionPool(
            sync_pool=sync_pool,
            async_pool=async_pool
        )

        return HttpSource(settings=settings, session_pool=pool)