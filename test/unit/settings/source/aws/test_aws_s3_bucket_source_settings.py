import pytest
import json

from templisafe.settings.source.source_settings import (
    SourceSettings,
    SourceKind,
)
from templisafe.settings.source.aws.aws_s3_bucket_source_settings import AwsS3BucketSourceSettings
from templisafe.exceptions.settings_error import SettingsError

# -----------------------------
# Fixtures / example configs
# -----------------------------
S3_CONFIG_DICT = {
    "kind": "aws_s3_bucket",
    "bucket": "my-bucket",
    "key": "my-key",
    "aws_access_key_id": "AKIAFAKE",
    "aws_secret_access_key": "SECRETFAKE",
    "region_name": "us-east-1",
    "endpoint_url": "http://localhost:4566"
}

S3_YAML = """
kind: aws_s3_bucket
bucket: my-bucket
key: my-key
aws_access_key_id: AKIAFAKE
aws_secret_access_key: SECRETFAKE
region_name: us-east-1
endpoint_url: http://localhost:4566
"""

S3_JSON = json.dumps(S3_CONFIG_DICT)


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_s3_only_required():
    instance = AwsS3BucketSourceSettings(
        bucket="my-bucket",
        key="my-key",
    )

    assert isinstance(instance, AwsS3BucketSourceSettings)
    assert instance.kind == SourceKind.AWS_S3_BUCKET
    assert instance.bucket == "my-bucket"
    assert instance.key == "my-key"

def test_create_s3_from_dict():
    instance = SourceSettings.create(**S3_CONFIG_DICT)
    assert isinstance(instance, AwsS3BucketSourceSettings)
    assert instance.kind == SourceKind.AWS_S3_BUCKET
    assert instance.bucket == "my-bucket"
    assert instance.key == "my-key"
    assert instance.aws_access_key_id == "AKIAFAKE"
    assert instance.aws_secret_access_key == "SECRETFAKE"
    assert instance.region_name == "us-east-1"
    assert instance.endpoint_url == "http://localhost:4566"

def test_create_missing_required_field_raises():
    cfg = S3_CONFIG_DICT.copy()
    cfg.pop("bucket")
    with pytest.raises(ValueError, match="Invalid fields"):
        SourceSettings.create(**cfg)

def test_create_extra_field_raises():
    cfg = S3_CONFIG_DICT.copy()
    cfg["extra"] = 123          # type: ignore
    with pytest.raises(ValueError):
        SourceSettings.create(**cfg)


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_s3():
    instance = AwsS3BucketSourceSettings.from_dict(S3_CONFIG_DICT)
    assert isinstance(instance, AwsS3BucketSourceSettings)
    assert instance.bucket == "my-bucket"
    assert instance.key == "my-key"


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_s3():
    instance = AwsS3BucketSourceSettings.from_yaml(S3_YAML)
    assert isinstance(instance, AwsS3BucketSourceSettings)
    assert instance.bucket == "my-bucket"
    assert instance.key == "my-key"

def test_from_yaml_invalid_yaml_raises():
    invalid_yaml = "this: [unbalanced"
    with pytest.raises(SettingsError):
        AwsS3BucketSourceSettings.from_yaml(invalid_yaml)

def test_from_yaml_not_a_dict_raises():
    yaml_list = "- item1\n- item2"
    with pytest.raises(SettingsError):
        AwsS3BucketSourceSettings.from_yaml(yaml_list)


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_s3():
    instance = AwsS3BucketSourceSettings.from_json(S3_JSON)
    assert isinstance(instance, AwsS3BucketSourceSettings)
    assert instance.bucket == "my-bucket"
    assert instance.key == "my-key"

def test_from_json_invalid_json_raises():
    invalid_json = '{"foo": "bar",}'
    with pytest.raises(SettingsError):
        AwsS3BucketSourceSettings.from_json(invalid_json)

def test_from_json_not_a_dict_raises():
    json_list = '["a", "b"]'
    with pytest.raises(SettingsError):
        AwsS3BucketSourceSettings.from_json(json_list)
