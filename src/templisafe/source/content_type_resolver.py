from pathlib import Path
from types import MappingProxyType
from collections.abc import Mapping

from templisafe.settings.source import *
from templisafe.settings.source.aws.aws_ssm_parameter_source_settings import AwsSsmParameterSourceSettings
from templisafe.exceptions.source_error import ContentTypeResolutionError
from templisafe.util.util import ContentType

#---------------------------------------------------------------------------------------------
# Content type resolver
#---------------------------------------------------------------------------------------------

CONTENT_TYPE_MAP: Mapping[str, ContentType] = MappingProxyType({
    ".j2": ContentType.TEXT,
    ".jinja": ContentType.TEXT,
    ".txt": ContentType.TEXT,
    ".yaml": ContentType.YAML,
    ".json": ContentType.JSON,
    ".toml": ContentType.TOML,
    ".xml": ContentType.XML,
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
            case SourceKind.AWS_S3_BUCKET:
                assert isinstance(settings, AwsS3BucketSourceSettings)
                return settings.key
            case SourceKind.AWS_SECRETS_MANAGER:
                assert isinstance(settings, AwsSecretsManagerSourceSettings)
                return settings.secret_id
            case SourceKind.AWS_SSM_PARAMETER:
                assert isinstance(settings, AwsSsmParameterSourceSettings)
                return settings.parameter_name
            case SourceKind.AWS_DYNAMODB:
                assert isinstance(settings, AwsDynamoDBSourceSettings)
                return None
            case SourceKind.HTTP:
                assert isinstance(settings, HttpSourceSettings)
                return None
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
        if not ext in self._content_type_map:
            raise ContentTypeResolutionError(settings)
        
        return self._content_type_map[ext]