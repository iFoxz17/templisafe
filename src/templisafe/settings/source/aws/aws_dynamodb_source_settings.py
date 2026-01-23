from overrides import overrides
from pydantic import Field, model_validator

from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.settings.source.source_settings import SourceSettings, SourceKind

class AwsDynamoDBSourceSettings(AwsSourceSettings):
    """
    Settings for reading an item from AWS DynamoDB. 
    The source `content_type` must be explicitly set.
    """

    table_name: str = Field(..., description="The name of the DynamoDB table")
    key: tuple[tuple[str, str], ...] = Field(
        ..., description="The primary key as a tuple of (name, value) pairs"
    )
    projection_expression: str | None = Field(
        default=None, description="Optional projection expression to select attributes"
    )

    @property
    def key_dict(self) -> dict[str, str]:
        return {k: v for k, v in self.key}

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.AWS_DYNAMODB

    @model_validator(mode="before")
    def transform_key_dict(cls, values):
        key = values.get("key")
        if isinstance(key, dict):
            # Convert dict to tuple of tuples
            values["key"] = tuple((k, str(v)) for k, v in key.items())
        return values

SourceSettings.register_source_kind(SourceKind.AWS_DYNAMODB, AwsDynamoDBSourceSettings)
