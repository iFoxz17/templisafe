from overrides import overrides

from templisafe.exceptions.source_error import AwsSourceError
from templisafe.settings.source.aws.aws_ssm_parameter_source_settings import (
    AwsSsmParameterSourceSettings,
)
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.aws.aws_source import AwsSource


class AwsSsmParameterSource(AwsSource):
    """Reads a parameter from AWS SSM Parameter Store lazily, only connecting on read()."""

    def __init__(self, settings: AwsSsmParameterSourceSettings) -> None:
        super().__init__(settings)

    @property
    def parameter_name(self) -> str:
        assert isinstance(self._settings, AwsSsmParameterSourceSettings)
        return self._settings.parameter_name

    @overrides
    def read(self) -> str:
        client = self._get_client("ssm")
        ClientError = self._client_error_type()
        settings: SourceSettings = self._settings
        assert isinstance(settings, AwsSsmParameterSourceSettings)

        try:
            resp = client.get_parameter(
                Name=settings.parameter_name,
                WithDecryption=settings.with_decryption,
            )
            value = resp.get("Parameter", {}).get("Value")
            if value is None:
                raise AwsSourceError(f"Failed to read AWS SSM parameter: parameter {self.parameter_name} has no value")
            return value
        except ClientError as e:
            raise AwsSourceError(f"Failed to read AWS SSM parameter: {settings.parameter_name}") from e
