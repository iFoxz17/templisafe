from typing import Any
from overrides import overrides
from threading import Lock
import boto3
from botocore.exceptions import ClientError

from templisafe.source.source import Source
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source.s3_source_settings import S3SourceSettings
from templisafe.exceptions.source_error import S3SourceError


class S3Source(Source):
    """Reads content from an S3 bucket lazily, only connecting on read()."""

    __slots__: tuple[str, ...] = ("_client", "_client_lock")

    def __init__(self, settings: S3SourceSettings) -> None:
        super().__init__(settings)
        assert isinstance(settings, S3SourceSettings)
        self._client: Any = None              # Lazy initialization on first read
        self._client_lock: Lock = Lock()      # Lock to avoid race conditions on the lazy initialization

    @property
    def bucket(self) -> str:
        assert isinstance(self._settings, S3SourceSettings)
        return self._settings.bucket

    @property
    def key(self) -> str:
        assert isinstance(self._settings, S3SourceSettings)
        return self._settings.key

    def _get_client(self) -> Any:
        """Initialize the boto3 client lazily."""
        settings: SourceSettings = self._settings
        assert isinstance(settings, S3SourceSettings)

        if self._client is None:
            with self._client_lock:
                if self._client is None:
                    self._client = boto3.client(
                        "s3",
                        aws_access_key_id=settings.aws_access_key_id,
                        aws_secret_access_key=settings.aws_secret_access_key,
                        region_name=settings.region_name,
                        endpoint_url=settings.endpoint_url,
                    )
        return self._client

    @overrides
    def read(self) -> str:
        """Fetch the object from S3 and return its content as a string."""
        client = self._get_client()
        try:
            resp = client.get_object(Bucket=self.bucket, Key=self.key)
            body: Any = resp.get("Body")
            if body is None:
                raise S3SourceError(self.bucket, self.key)
            return body.read().decode("utf-8")
        except ClientError as e:
            raise S3SourceError(self.bucket, self.key) from e
