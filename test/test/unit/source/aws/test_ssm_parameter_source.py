import boto3
import pytest
from moto import mock_aws

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import AwsSourceError
from templisafe.settings.source.aws.aws_ssm_parameter_source_settings import (
    AwsSsmParameterSourceSettings,
)
from templisafe.source.aws.aws_ssm_parameter_source import AwsSsmParameterSource

# -------------------------------------------------------------------
# Constants for the test
# -------------------------------------------------------------------
TEST_PARAMETER_NAME = "/my/app/parameter"
TEST_PARAMETER_VALUE = "super-secret-value"


# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------
@pytest.fixture
def ssm_settings() -> AwsSsmParameterSourceSettings:
    """SSM settings pointing to the mock parameter."""
    return AwsSsmParameterSourceSettings(
        content_type=ContentType.TEXT,
        parameter_name=TEST_PARAMETER_NAME,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
        endpoint_url=None,  # Moto handles endpoints internally
    )


@pytest.fixture
def moto_ssm():
    with mock_aws():
        client = boto3.client("ssm", region_name="us-east-1")
        client.put_parameter(
            Name=TEST_PARAMETER_NAME,
            Value=TEST_PARAMETER_VALUE,
            Type="SecureString",  # Encrypted
        )
        yield


@pytest.fixture
def moto_ssm_not_encrypted():
    with mock_aws():
        client = boto3.client("ssm", region_name="us-east-1")
        # Put a plain String parameter instead of SecureString
        client.put_parameter(
            Name=TEST_PARAMETER_NAME,
            Value=TEST_PARAMETER_VALUE,
            Type="String",  # Not encrypted
        )
        yield


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------
def test_read_returns_content(moto_ssm, ssm_settings):
    """Test that AwsSsmParameterSource.read() returns the correct value."""
    source = AwsSsmParameterSource(ssm_settings)
    content = source.read()
    assert content == TEST_PARAMETER_VALUE


def test_client_uses_settings_credentials(moto_ssm):
    settings = AwsSsmParameterSourceSettings(
        content_type=ContentType.TEXT,
        parameter_name=TEST_PARAMETER_NAME,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )

    source = AwsSsmParameterSource(settings)

    assert source._client is None
    source.read()

    client = source._client
    creds = client._request_signer._credentials

    assert creds.access_key == "FAKE_KEY"
    assert creds.secret_key == "FAKE_SECRET"


def test_boto3_resolves_env_credentials(moto_ssm, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "REAL_ACCESS_KEY")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "REAL_SECRET_KEY")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # Let boto3 resolve credentials automatically
    settings = AwsSsmParameterSourceSettings(content_type=ContentType.TEXT, parameter_name=TEST_PARAMETER_NAME)

    source = AwsSsmParameterSource(settings)
    source.read()

    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()

    assert creds.access_key == "REAL_ACCESS_KEY"
    assert creds.secret_key == "REAL_SECRET_KEY"


def test_read_raises_on_missing_parameter(moto_ssm):
    """Test that reading a non-existent parameter raises S3SourceError."""
    source = AwsSsmParameterSource(
        AwsSsmParameterSourceSettings(
            content_type=ContentType.TEXT,
            parameter_name="/missing/parameter",
            aws_access_key_id="FAKE_KEY",
            aws_secret_access_key="FAKE_SECRET",
            region_name="us-east-1",
        )
    )

    with pytest.raises(AwsSourceError):
        source.read()


def test_read_with_decryption_disabled(moto_ssm_not_encrypted):
    """Test that with_decryption=False is passed correctly."""

    settings = AwsSsmParameterSourceSettings(
        content_type=ContentType.TEXT,
        parameter_name=TEST_PARAMETER_NAME,
        with_decryption=False,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )

    source = AwsSsmParameterSource(settings)
    content = source.read()

    assert content == TEST_PARAMETER_VALUE
