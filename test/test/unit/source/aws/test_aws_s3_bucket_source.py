import boto3
import pytest
from moto import mock_aws

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import AwsSourceError
from templisafe.settings.source.aws.aws_s3_bucket_source_settings import (
    AwsS3BucketSourceSettings,
)
from templisafe.source.aws.aws_s3_bucket_source import AwsS3BucketSource

# -------------------------------------------------------------------
# Constants for the test
# -------------------------------------------------------------------
TEST_BUCKET = "my-bucket"
TEST_KEY = "test.txt"
TEST_CONTENT = "Hello Moto!"


@pytest.fixture
def s3_settings() -> AwsS3BucketSourceSettings:
    """S3 settings pointing to the mock S3 bucket."""
    return AwsS3BucketSourceSettings(
        content_type=ContentType.TEXT,
        bucket=TEST_BUCKET,
        key=TEST_KEY,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
        endpoint_url=None,  # Moto does not need a custom endpoint
    )


# -------------------------------------------------------------------
# Moto fixture for mocking S3
# -------------------------------------------------------------------
@pytest.fixture
def moto_s3_bucket():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=TEST_BUCKET)
        # Upload a test object
        client.put_object(Bucket=TEST_BUCKET, Key=TEST_KEY, Body=TEST_CONTENT.encode("utf-8"))
        yield


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------


def test_read_returns_content(moto_s3_bucket, s3_settings):
    """Test that S3Source.read() returns the correct content."""
    source = AwsS3BucketSource(s3_settings)
    content = source.read()
    assert content == TEST_CONTENT


def test_read_with_env_credentials(moto_s3_bucket, monkeypatch):
    """
    Test reading from S3 when credentials are provided via environment
    variables (simulating real AWS credentials / IAM role usage).
    """

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "REALISTIC_ACCESS_KEY")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "REALISTIC_SECRET_KEY")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # let boto3 resolve aws_access_key_id, aws_secret_access_key and region_name
    settings = AwsS3BucketSourceSettings(
        content_type=ContentType.TEXT,
        bucket=TEST_BUCKET,
        key=TEST_KEY,
    )

    source = AwsS3BucketSource(settings)
    content = source.read()

    assert content == TEST_CONTENT


def test_client_uses_settings_credentials(moto_s3_bucket):
    settings = AwsS3BucketSourceSettings(
        content_type=ContentType.TEXT,
        bucket=TEST_BUCKET,
        key=TEST_KEY,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )

    source = AwsS3BucketSource(settings)

    assert source._client is None
    source.read()
    client = source._client
    creds = client._request_signer._credentials
    assert creds.access_key == "FAKE_KEY"
    assert creds.secret_key == "FAKE_SECRET"


def test_boto3_resolves_env_credentials(moto_s3_bucket, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "REAL_ACCESS_KEY")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "REAL_SECRET_KEY")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # let boto3 resolve aws_access_key_id, aws_secret_access_key and region_name
    settings = AwsS3BucketSourceSettings(
        content_type=ContentType.TEXT,
        bucket=TEST_BUCKET,
        key=TEST_KEY,
    )

    source = AwsS3BucketSource(settings)
    source.read()

    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()

    assert creds.access_key == "REAL_ACCESS_KEY"
    assert creds.secret_key == "REAL_SECRET_KEY"


def test_read_raises_on_missing_bucket(moto_s3_bucket):
    """Test that reading a non-existent object raises S3SourceError."""
    source = AwsS3BucketSource(
        AwsS3BucketSourceSettings(
            content_type=ContentType.TEXT,
            bucket="missing-bucket",  # This bucket does not exist
            key=TEST_KEY,
            aws_access_key_id="FAKE_KEY",
            aws_secret_access_key="FAKE_SECRET",
            region_name="us-east-1",
        )
    )

    with pytest.raises(AwsSourceError):
        source.read()


def test_read_raises_on_missing_object(moto_s3_bucket):
    """Test that reading a non-existent object raises S3SourceError."""
    source = AwsS3BucketSource(
        AwsS3BucketSourceSettings(
            content_type=ContentType.TEXT,
            bucket=TEST_BUCKET,
            key="missing.txt",  # This object does not exist
            aws_access_key_id="FAKE_KEY",
            aws_secret_access_key="FAKE_SECRET",
            region_name="us-east-1",
        )
    )

    with pytest.raises(AwsSourceError):
        source.read()
