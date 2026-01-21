from overrides import overrides

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceSettings, SourceKind

class AwsSecretsManagerSourceSettings(AwsSourceSettings):
    """
    Settings for reading a secret from AWS Secrets Manager.
    """

    secret_id: str
    version_id: str | None = None
    version_stage: str | None = None

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_SECRETS_MANAGER


# Register subclass
SourceSettings.register_source_kind(SourceKind.AWS_SECRETS_MANAGER, AwsSecretsManagerSourceSettings)
