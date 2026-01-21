from overrides import overrides

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceSettings, SourceKind


class AwsSsmParameterSourceSettings(AwsSourceSettings):
    """
    Settings for reading a parameter from AWS SSM Parameter Store.
    """

    parameter_name: str
    with_decryption: bool = True  # default to decrypt secure strings

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_SSM_PARAMETER


# Register subclass
SourceSettings.register_source_kind(SourceKind.AWS_SSM_PARAMETER, AwsSsmParameterSourceSettings)