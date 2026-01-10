from pathlib import Path
from types import MappingProxyType
from collections.abc import Mapping

from templisafe.settings.source_settings import (
    SourceSettings, 
    LocalSourceSettings, 
    InlineSourceSettings, 
    SourceKind
)
from templisafe.source.source import Source
from templisafe.source.local_source import LocalSource
from templisafe.source.inline_source import InlineSource, InlineSourceSettings
from templisafe.exceptions.source_error import UnsupportedSourceError, ContentTypeResolutionError
from templisafe.util.util import ContentType

#---------------------------------------------------------------------------------------------
# Content type resolver
#---------------------------------------------------------------------------------------------

CONTENT_TYPE_MAP: Mapping[str, ContentType] = MappingProxyType({
    ".j2": ContentType.JINJA,
    ".jinja": ContentType.JINJA,
    ".yaml": ContentType.YAML,
})

class ContentTypeResolver:
    __slots__: tuple[str, ...] = ("_content_type_map",)

    def __init__(self, content_type_map: Mapping[str, ContentType] | None = None) -> None:
        self._content_type_map: Mapping[str, ContentType] = content_type_map or CONTENT_TYPE_MAP

    @staticmethod
    def _extract_extension(path: Path | str) -> str:
        """Return lowercase suffix including the dot, or empty string if none."""
        if isinstance(path, Path):
            return path.suffix.lower()
        dot: int = path.rfind(".")
        return path[dot:].lower() if dot != -1 else ""

    @staticmethod
    def _extract_source_path(settings: SourceSettings) -> Path | str | None:
        """Return the path to inspect for content type, or None if not applicable."""
        match settings.kind:
            case SourceKind.LOCAL:
                assert isinstance(settings, LocalSourceSettings)
                return settings.path
            case SourceKind.INLINE:
                assert isinstance(settings, InlineSourceSettings)
                return None
            case _:
                return None

    def resolve(self, settings: SourceSettings) -> ContentType:
        """Resolve content type from settings or raise ContentTypeResolutionError."""
        path: Path | str | None = self._extract_source_path(settings)
        if path is None:
            raise ContentTypeResolutionError(settings)

        ext: str = self._extract_extension(path)
        try:
            return self._content_type_map[ext]
        except KeyError as exc:
            raise ContentTypeResolutionError(settings) from exc

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class SourceFactory:
    _SOURCE_MAP: Mapping[type[SourceSettings], type[Source]] = MappingProxyType(
        {
            InlineSourceSettings: InlineSource,
            LocalSourceSettings: LocalSource,
        }
    )
    
    def create(self, settings: SourceSettings) -> Source:
        source_type: type[Source] | None = SourceFactory._SOURCE_MAP.get(type(settings))
        if source_type is None:
            raise UnsupportedSourceError(settings)
        return source_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class SourceManager:
    __slots__: tuple[str, ...] = ("_factory", "_resolver", "_sources")

    def __init__(self, sources: dict[SourceSettings, Source] | None = None) -> None:
        self._factory: SourceFactory = SourceFactory()
        self._resolver: ContentTypeResolver = ContentTypeResolver()
        self._sources: dict[SourceSettings, Source] = sources or {}
    
    def get_or_create(self, settings: SourceSettings) -> Source:
        if settings.content_type is None:
            content_type: ContentType = self._resolver.resolve(settings)
            settings = settings.model_copy(update={"content_type": content_type})

        s: dict[SourceSettings, Source] = self._sources
        if settings not in s:
            s[settings] = self._factory.create(settings)
        return s[settings]

    def __contains__(self, settings: SourceSettings) -> bool:
        return settings in self._sources