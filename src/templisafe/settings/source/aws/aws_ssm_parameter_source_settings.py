from overrides import overrides
from pydantic import Field

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings


class AwsSsmParameterSourceSettings(AwsSourceSettings):
    """
    Settings for reading a parameter from AWS SSM Parameter Store.
    The source `content_type` can be inferred from the `parameter_name` extension, if present.
    """

    parameter_name: str = Field(..., description="The name of the SSM parameter")
    with_decryption: bool = Field(default=True, description="Whether to decrypt secure string parameters")

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_SSM_PARAMETER


SourceSettings.register_source_kind(SourceKind.AWS_SSM_PARAMETER, AwsSsmParameterSourceSettings)
