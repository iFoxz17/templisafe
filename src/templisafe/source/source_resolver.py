from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.source import Source
from templisafe.source.source_manager import SourceManager

#---------------------------------------------------------------------------------------------
# Resolver
#---------------------------------------------------------------------------------------------

class SourceResolver:
    __slots__ = ("_source_manager", "_content_type_resolver")

    def __init__(
        self,
        source_manager: SourceManager,
        content_type_resolver: ContentTypeResolver | None = None,
    ) -> None:
        self._source_manager: SourceManager = source_manager
        self._content_type_resolver: ContentTypeResolver = content_type_resolver or ContentTypeResolver()

    def _resolve_content_type(self, settings: SourceSettings) -> SourceSettings:
        if settings.content_type is None:
            return settings.model_copy(
                update={"content_type": self._content_type_resolver.resolve(settings)}
            )
        return settings

    def resolve(self, source: Source | SourceSettings) -> Source:
        if isinstance(source, Source):
            return source
        return self._source_manager.get_or_create(self._resolve_content_type(source))

    def resolve_optional(self, source: Source | SourceSettings | None) -> Source | None:
        return None if source is None else self.resolve(source)