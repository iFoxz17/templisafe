from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.source import Source
from templisafe.source.source_manager import SourceManager

class SourceResolver:
    """Resolves `Source` instances."""

    __slots__: tuple[str, ...] = ("_source_manager", "_content_type_resolver")

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
        """
        Resolve a `Source` instance.

        Parameters
        ----------
        source : Source | SourceSettings
            Either an existing `Source` instance or a `SourceSettings` object.

        Returns
        -------
        Source
            The resolved `Source` instance.
        """

        if isinstance(source, Source):
            return source
        return self._source_manager.get_or_create(self._resolve_content_type(source))

    def resolve_optional(self, source: Source | SourceSettings | None) -> Source | None:
        """
        Resolve a `Source` instance, returning None if the input is None.

        Parameters
        ----------
        source : Source | SourceSettings | None
            Either an existing `Source`, a `SourceSettings` object or None.

        Returns
        -------
        Source | None
            The resolved `Source` instance, or None if the input was None.
        """
        return None if source is None else self.resolve(source)