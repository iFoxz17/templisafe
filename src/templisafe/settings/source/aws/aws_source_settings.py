from abc import ABC
from pydantic import Field

from templisafe.settings.source.source_settings import SourceSettings

class AwsSourceSettings(SourceSettings, ABC):
    """Base settings shared by all AWS-backed sources."""

    aws_access_key_id: str | None = Field(
        default=None,
        description="AWS access key ID"
    )
    aws_secret_access_key: str | None = Field(
        default=None,
        description="AWS secret access key"
    )
    aws_session_token: str | None = Field(
        default=None,
        description="AWS session token"
    )

    region_name: str | None = Field(
        default=None,
        description="AWS region name"
    )
    endpoint_url: str | None = Field(
        default=None,
        description="Custom AWS endpoint URL (e.g. for LocalStack)"
    )

    @property
    def boto3_kwargs(self) -> dict[str, str | None]:
        return {
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
            "aws_session_token": self.aws_session_token,
            "region_name": self.region_name,
            "endpoint_url": self.endpoint_url,
        }
