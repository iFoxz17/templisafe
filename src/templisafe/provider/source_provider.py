from templisafe.content.content import ContentType
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.source import Source
from templisafe.source.source_resolver import SourceResolver


class SourceProvider:
    """Provides `Source` instances from either `Source` objects or `SourceSettings` configurations."""

    __slots__: tuple[str, ...] = ("_source_resolver", "_content_type_resolver")

    def __init__(
        self,
        source_resolver: SourceResolver,
        content_type_resolver: ContentTypeResolver,
    ) -> None:
        self._source_resolver: SourceResolver = source_resolver
        self._content_type_resolver: ContentTypeResolver = content_type_resolver

    def provide(self, source: Source | SourceSettings) -> Source:
        """
        Provide a `Source` instance from the given input.

        Parameters
        ----------
        source : Source | SourceSettings
            Either a fully constructed `Source` or a `SourceSettings` configuration.

        Returns
        -------
        Source
            The source instance, with content type inferred if necessary.
        """

        if isinstance(source, SourceSettings):
            if not source.has_content_type:
                content_type: ContentType = self._content_type_resolver.resolve(source)
                source = source.model_copy(update={"content_type": content_type})

        return self._source_resolver.resolve(source)
