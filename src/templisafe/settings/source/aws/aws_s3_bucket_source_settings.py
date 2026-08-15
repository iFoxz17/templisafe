from overrides import overrides
from pydantic import Field

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings


class AwsS3BucketSourceSettings(AwsSourceSettings):
    """
    Settings for reading an object from an AWS S3 bucket.
    The source `content_type` can be inferred from the `key` extension, if present.
    """

    bucket: str = Field(..., description="The name of the S3 bucket")
    key: str = Field(..., description="The key/path of the object in the bucket")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_S3_BUCKET


SourceSettings.register_source_kind(SourceKind.AWS_S3_BUCKET, AwsS3BucketSourceSettings)
