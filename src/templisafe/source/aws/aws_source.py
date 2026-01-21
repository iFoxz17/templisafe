from typing import Any
from abc import ABC
from threading import Lock
import boto3

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.source.source import Source
from templisafe.settings.source.aws.aws_s3_bucket_source_settings import AwsS3BucketSourceSettings

class AwsSource(Source, ABC):
    
    __slots__: tuple[str, ...] = ("_client", "_client_lock")

    def __init__(self, settings: AwsSourceSettings) -> None:
        super().__init__(settings)
        
        self._client: Any = None              # Lazy initialization on first read
        self._client_lock: Lock = Lock()      # Lock to avoid race conditions on the lazy initialization

    @property
    def settings(self) -> AwsSourceSettings:
        assert isinstance(self._settings, AwsSourceSettings)
        return self._settings

    def _get_client(self, aws_service: str, **kwargs) -> Any:
        """Initialize the boto3 client lazily."""

        boto3_kwargs: dict[str, str] = {
            k: v 
            for k, v in self.settings.boto3_kwargs.items()
            if v is not None
        }
        boto3_kwargs.update(kwargs)

        if self._client is None:
            with self._client_lock:
                if self._client is None:
                    self._client = boto3.client(
                        aws_service,
                        **boto3_kwargs
                    )
        return self._client