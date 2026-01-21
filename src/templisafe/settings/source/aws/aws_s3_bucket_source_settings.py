from overrides import overrides

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings

class AwsS3BucketSourceSettings(AwsSourceSettings):
    bucket: str
    key: str

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_S3_BUCKET


# Register subclass
SourceSettings.register_source_kind(SourceKind.AWS_S3_BUCKET, AwsS3BucketSourceSettings)
