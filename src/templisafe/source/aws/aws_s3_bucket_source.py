from typing import Any
from overrides import overrides
from botocore.exceptions import ClientError

from templisafe.settings.source.aws.aws_s3_bucket_source_settings import AwsS3BucketSourceSettings
from templisafe.source.aws.aws_source import AwsSource
from templisafe.exceptions.source_error import AwsSourceError


class AwsS3BucketSource(AwsSource):
    """Reads content from an S3 bucket lazily, only connecting on read()."""

    def __init__(self, settings: AwsS3BucketSourceSettings) -> None:
        super().__init__(settings)
        
    @property
    def bucket(self) -> str:
        assert isinstance(self.settings, AwsS3BucketSourceSettings)
        return self.settings.bucket

    @property
    def key(self) -> str:
        assert isinstance(self.settings, AwsS3BucketSourceSettings)
        return self.settings.key

    @overrides
    def read(self) -> str:
        client: Any = self._get_client("s3")
        try:
            resp = client.get_object(Bucket=self.bucket, Key=self.key)
            body: Any = resp.get("Body")
            if body is None:
                raise AwsSourceError(
                    f"Failed to read AWS S3 bucket object (bucket={self.bucket}, key={self.key}): "
                    "response body is None"
                    )
            return body.read().decode("utf-8")
        except ClientError as e:
            raise AwsSourceError(
                    f"Failed to read AWS S3 bucket object (bucket={self.bucket}, key={self.key})"
                    ) from e
