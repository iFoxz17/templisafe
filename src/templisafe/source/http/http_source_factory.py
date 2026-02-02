from templisafe.settings.source.http.http_async_session_settings import HttpAsyncSessionSettings
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.settings.source.http.http_sync_session_settings import HttpSyncSessionSettings

from .http_source import HttpSource, HttpSessionPool, SyncSessionPool, HttpAsyncSessionPool
from .sync.http_sync_session_manager import HttpSyncSessionManager
from .async_.http_async_session_pool import HttpAsyncSessionManager

class HttpSourceFactory:
    """Creates `HttpSource` instances from http source settings."""
        
    def create(self, settings: HttpSourceSettings) -> HttpSource:
        """Create a `HttpSource` instance for the given settings."""

        sync_settings: HttpSyncSessionSettings = settings.sync_session_settings
        async_settings: HttpAsyncSessionSettings = settings.async_session_settings

        sync_manager: HttpSyncSessionManager = HttpSyncSessionManager(sync_settings) 
        async_manager: HttpAsyncSessionManager = HttpAsyncSessionManager(async_settings)

        sync_pool: SyncSessionPool = SyncSessionPool(
            manager=sync_manager,
            max_connections=sync_settings.pool_connections * sync_settings.pool_maxsize,
            max_slots=sync_settings.max_slots
        ) 

        async_pool: HttpAsyncSessionPool = HttpAsyncSessionPool(
            manager=async_manager,
            max_users_per_session=1
        ) 

        pool: HttpSessionPool = HttpSessionPool(
            sync_pool=sync_pool,
            async_pool=async_pool
        )

        return HttpSource(
            settings=settings,
            session_pool=pool
        )

        