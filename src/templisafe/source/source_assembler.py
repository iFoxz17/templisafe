from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.source_manager import SourceFactory, SourceManager
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.source.source_resolver import SourceResolver

DEFAULT_MANAGER_SETTINGS: ManagerSettings = ManagerSettings(cache=True) 

class SourceAssembler:
    __slots__ : tuple[str, ...] = ()

    def assemble(self, manager_settings: ManagerSettings | None = None) -> SourceResolver:
        factory: SourceFactory = SourceFactory()
        manager: SourceManager = SourceManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS,
            factory=factory
        )
        content_type_resolver: ContentTypeResolver = ContentTypeResolver()
        resolver: SourceResolver = SourceResolver(
            source_manager=manager,
            content_type_resolver=content_type_resolver
        )

        return resolver
