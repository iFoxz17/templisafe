import pytest
import boto3
from moto import mock_aws

from templisafe.content.content import ContentType
from templisafe.source.aws.aws_secrets_manager_source import AwsSecretsManagerSource
from templisafe.settings.source.aws.aws_secrets_manager_source_settings import AwsSecretsManagerSourceSettings
from templisafe.exceptions.source_error import AwsSourceError  # replace with proper error later if needed

# -------------------------------------------------------------------
# Constants for the test
# -------------------------------------------------------------------
TEST_SECRET_ID = "myapp/secret.json"
TEST_SECRET_VALUE = '{"username":"admin","password":"1234"}'

@pytest.fixture
def secrets_manager_settings() -> AwsSecretsManagerSourceSettings:
    """Secrets Manager settings pointing to the mock secret."""
    return AwsSecretsManagerSourceSettings(
        content_type=ContentType.TEXT,
        secret_id=TEST_SECRET_ID,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
        endpoint_url=None,  # Moto handles endpoints internally
    )

# -------------------------------------------------------------------
# Moto fixture for mocking Secrets Manager
# -------------------------------------------------------------------
@pytest.fixture
def moto_secrets_manager():
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="us-east-1")
        # Create the secret
        client.create_secret(Name=TEST_SECRET_ID, SecretString=TEST_SECRET_VALUE)
        yield

# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_read_returns_content(moto_secrets_manager, secrets_manager_settings):
    """Test that AwsSecretsManagerSource.read() returns the correct secret content."""
    source = AwsSecretsManagerSource(secrets_manager_settings)
    content = source.read()
    assert content == TEST_SECRET_VALUE

def test_client_uses_settings_credentials(moto_secrets_manager):
    settings = AwsSecretsManagerSourceSettings(
        content_type=ContentType.TEXT,
        secret_id=TEST_SECRET_ID,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )

    source = AwsSecretsManagerSource(settings)
    
    assert source._client is None
    source.read()
    client = source._client
    creds = client._request_signer._credentials
    assert creds.access_key == "FAKE_KEY"
    assert creds.secret_key == "FAKE_SECRET"

def test_boto3_resolves_env_credentials(moto_secrets_manager, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "REAL_ACCESS_KEY")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "REAL_SECRET_KEY")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # let boto3 resolve aws_access_key_id, aws_secret_access_key and region_name
    settings = AwsSecretsManagerSourceSettings(secret_id=TEST_SECRET_ID, content_type=ContentType.TEXT)
    source = AwsSecretsManagerSource(settings)
    source.read()

    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()

    assert creds.access_key == "REAL_ACCESS_KEY"
    assert creds.secret_key == "REAL_SECRET_KEY"

def test_read_raises_on_missing_secret(moto_secrets_manager):
    """Test that reading a non-existent secret raises S3SourceError."""
    source = AwsSecretsManagerSource(AwsSecretsManagerSourceSettings(
        content_type=ContentType.TEXT,
        secret_id="missing-secret",
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1"
    ))

    with pytest.raises(AwsSourceError):
        source.read()

def test_read_with_version_stage(moto_secrets_manager):
    """Test that version_stage is passed to get_secret_value."""
    settings = AwsSecretsManagerSourceSettings(
        content_type=ContentType.TEXT,
        secret_id=TEST_SECRET_ID,
        version_stage="AWSCURRENT",
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1"
    )

    source = AwsSecretsManagerSource(settings)
    content = source.read()
    assert content == TEST_SECRET_VALUE
