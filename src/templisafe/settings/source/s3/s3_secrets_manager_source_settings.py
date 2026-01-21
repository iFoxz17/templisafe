from overrides import overrides

from templisafe.settings.source.source_settings import SourceSettings, SourceKind


class SecretsManagerSourceSettings(SourceSettings):
    """
    Settings for reading a secret from AWS Secrets Manager.
    """

    secret_id: str
    version_id: str | None = None
    version_stage: str | None = None

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None

    region_name: str | None = None
    endpoint_url: str | None = None

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_SECRETS_MANAGER


# Register subclass
SourceSettings.register_source_kind(SourceKind.AWS_SECRETS_MANAGER, SecretsManagerSourceSettings)
