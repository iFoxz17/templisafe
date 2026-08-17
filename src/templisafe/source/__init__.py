from templisafe.source.http.http_source import HttpSource
from templisafe.source.inline_source import InlineSource
from templisafe.source.local_source import LocalSource
from templisafe.source.source import Source

_AWS_EXPORTS: dict[str, str] = {
    "AwsSource": "templisafe.source.aws.aws_source",
    "AwsDynamoDBSource": "templisafe.source.aws.aws_dynamodb_source",
    "AwsS3BucketSource": "templisafe.source.aws.aws_s3_bucket_source",
    "AwsSecretsManagerSource": "templisafe.source.aws.aws_secrets_manager_source",
    "AwsSsmParameterSource": "templisafe.source.aws.aws_ssm_parameter_source",
}


def __getattr__(name: str):
    if name not in _AWS_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    value = getattr(import_module(_AWS_EXPORTS[name]), name)
    globals()[name] = value
    return value


__all__ = [
    "Source",
    "InlineSource",
    "LocalSource",
    "HttpSource",
]
