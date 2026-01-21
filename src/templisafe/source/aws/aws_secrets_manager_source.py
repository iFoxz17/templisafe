from typing import Any
from overrides import overrides
from botocore.exceptions import ClientError

from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source.aws.aws_secrets_manager_source_settings import AwsSecretsManagerSourceSettings
from templisafe.source.aws.aws_source import AwsSource
from templisafe.exceptions.source_error import AwsSourceError


class AwsSecretsManagerSource(AwsSource):
    """
    Reads a secret from AWS Secrets Manager lazily, only connecting on read().
    """

    def __init__(self, settings: AwsSecretsManagerSourceSettings) -> None:
        super().__init__(settings)

    @property
    def secret_id(self) -> str:
        assert isinstance(self._settings, AwsSecretsManagerSourceSettings)
        return self._settings.secret_id

    @overrides
    def read(self) -> str:
        client: Any = self._get_client("secretsmanager")

        try:
            kwargs: dict[str, Any] = {"SecretId": self.secret_id}

            settings: SourceSettings = self._settings
            assert isinstance(settings, AwsSecretsManagerSourceSettings)

            if settings.version_id is not None:
                kwargs["VersionId"] = settings.version_id

            if settings.version_stage is not None:
                kwargs["VersionStage"] = settings.version_stage

            resp = client.get_secret_value(**kwargs)

            if "SecretString" in resp:
                return resp["SecretString"]

            if "SecretBinary" in resp:
                return resp["SecretBinary"].decode("utf-8")

            raise AwsSourceError(
                    f"Failed to read AWS secrets manager object: secret {self.secret_id} has no value"
                    )

        except ClientError as e:
            raise AwsSourceError(f"Failed to read AWS secrets manager object") from e
