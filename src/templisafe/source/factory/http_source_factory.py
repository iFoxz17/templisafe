from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.source.http.http_source import HttpSource
from templisafe.source.http.http_session_manager import (
    HttpAsyncSessionManager,
    HttpSessionManager, 
    HttpSyncSessionManager,
)

class HttpSourceFactory:
    """Creates `HttpSource` instances from http source settings."""
        
    def create(self, settings: HttpSourceSettings) -> HttpSource:
        """Create a `HttpSource` instance for the given settings."""

        sync_manager: HttpSyncSessionManager = HttpSyncSessionManager(settings.sync_session_settings) 
        async_manager: HttpAsyncSessionManager = HttpAsyncSessionManager(settings.async_session_settings)
        session_manager: HttpSessionManager = HttpSessionManager(
            sync_manager=sync_manager,
            async_manager=async_manager
        ) 

        return HttpSource(
            settings=settings,
            session_manager=session_manager
        )

        