import pytest
import boto3
from moto import mock_aws

from templisafe.source.s3_source import S3Source
from templisafe.settings.source.s3_source_settings import S3SourceSettings
from templisafe.exceptions.source_error import S3SourceError

# -------------------------------------------------------------------
# Constants for the test
# -------------------------------------------------------------------
TEST_BUCKET = "my-bucket"
TEST_KEY = "test.txt"
TEST_CONTENT = "Hello Moto!"

@pytest.fixture
def s3_settings() -> S3SourceSettings:
    """S3 settings pointing to the mock S3 bucket."""
    return S3SourceSettings(
        bucket=TEST_BUCKET,
        key=TEST_KEY,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
        endpoint_url=None  # Moto does not need a custom endpoint
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

@pytest.mark.s3
def test_read_returns_content(moto_s3_bucket, s3_settings):
    """Test that S3Source.read() returns the correct content."""
    source = S3Source(s3_settings)
    content = source.read()
    assert content == TEST_CONTENT

@pytest.mark.s3
def test_read_raises_on_missing_bucket(moto_s3_bucket):
    """Test that reading a non-existent object raises S3SourceError."""
    source = S3Source(S3SourceSettings(
        bucket="missing-bucket",  # This bucket does not exist
        key=TEST_KEY,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1"
    ))

    with pytest.raises(S3SourceError):
        source.read()

@pytest.mark.s3
def test_read_raises_on_missing_object(moto_s3_bucket):
    """Test that reading a non-existent object raises S3SourceError."""
    source = S3Source(S3SourceSettings(
        bucket=TEST_BUCKET,
        key="missing.txt",  # This object does not exist
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1"
    ))

    with pytest.raises(S3SourceError):
        source.read()