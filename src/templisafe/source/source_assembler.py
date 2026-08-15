from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.source_manager import SourceFactory, SourceManager
from templisafe.source.source_resolver import SourceResolver


class SourceAssembler:
    """Assembles a `SourceResolver` with all necessary components."""

    __slots__: tuple[str, ...] = ()

    def assemble(self, manager_settings: ManagerSettings | None = None) -> SourceResolver:
        """
        Create and return a fully initialized `SourceResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.

        Returns
        -------
        SourceResolver
            A `SourceResolver` ready to resolve sources.
        """

        factory: SourceFactory = SourceFactory()
        manager: SourceManager = SourceManager(settings=manager_settings or DEFAULT_MANAGER_SETTINGS, factory=factory)
        content_type_resolver: ContentTypeResolver = ContentTypeResolver()
        resolver: SourceResolver = SourceResolver(source_manager=manager, content_type_resolver=content_type_resolver)

        return resolver
