from abc import ABC
from templisafe.settings.source.source_settings import SourceSettings

class AwsSourceSettings(SourceSettings, ABC):
    """
    Base settings shared by all AWS-backed sources.
    """

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None

    region_name: str | None = None
    endpoint_url: str | None = None

    @property
    def boto3_kwargs(self) -> dict[str, str | None]:
        return {
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
            "aws_session_token": self.aws_session_token,
            "region_name": self.region_name,
            "endpoint_url": self.endpoint_url,
        }