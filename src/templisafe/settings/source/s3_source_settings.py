from overrides import overrides
from templisafe.settings.source.source_settings import SourceSettings, SourceKind

class S3SourceSettings(SourceSettings):
    bucket: str
    key: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    region_name: str | None = None
    endpoint_url: str | None = None

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.S3


# Register subclass
SourceSettings.register_source_kind(SourceKind.S3, S3SourceSettings)
