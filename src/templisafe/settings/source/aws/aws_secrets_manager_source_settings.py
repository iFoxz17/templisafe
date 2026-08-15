from overrides import overrides
from pydantic import Field

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings


class AwsSecretsManagerSourceSettings(AwsSourceSettings):
    """
    Settings for reading a secret from AWS Secrets Manager.
    The source `content_type` can be inferred from the `secret_id` extension, if present.
    """

    secret_id: str = Field(..., description="The ID or ARN of the secret")
    version_id: str | None = Field(default=None, description="The specific version ID of the secret (optional)")
    version_stage: str | None = Field(default=None, description="The staging label of the secret version (optional)")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_SECRETS_MANAGER


SourceSettings.register_source_kind(SourceKind.AWS_SECRETS_MANAGER, AwsSecretsManagerSourceSettings)
