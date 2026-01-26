import pytest

from templisafe.settings.source.aws import *
from templisafe.settings.source.custom_source_settings import CustomSourceSettings
from templisafe.settings.source.http_source_settings import HttpSourceSettings
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.settings.source.local_source_settings import LocalSourceSettings
from templisafe.exceptions.source_error import ContentTypeResolutionError
from templisafe.content.content import ContentType
from templisafe.source.content_type_resolver import ContentTypeResolver

# -----------------------------
# AWS common kwargs
# -----------------------------
AWS_COMMON_KWARGS = {
    "aws_access_key_id": "aws_access_key_id",
    "aws_secret_access_key": "aws_secret_access_key",
    "aws_session_token": "aws_session_token",
    "region_name": "us-east-1",
    "endpoint_url": "http://localhost:4566"
}

# -----------------------------
# AWS source fixtures
# -----------------------------
@pytest.fixture
def s3_settings() -> AwsS3BucketSourceSettings:
    return AwsS3BucketSourceSettings(
        content_type=None, bucket="my-bucket", key="my-key.yaml", **AWS_COMMON_KWARGS
    )

@pytest.fixture
def aws_secrets_manager_settings() -> AwsSecretsManagerSourceSettings:
    return AwsSecretsManagerSourceSettings(
        content_type=None, secret_id="secret_id.json", version_id="version_id",
        version_stage="version_stage", **AWS_COMMON_KWARGS
    )

@pytest.fixture
def aws_ssm_settings() -> AwsSsmParameterSourceSettings:
    return AwsSsmParameterSourceSettings(
        content_type=None, parameter_name="parameter_name.toml", with_decryption=True, **AWS_COMMON_KWARGS
    )

@pytest.fixture
def aws_dynamodb_settings() -> AwsDynamoDBSourceSettings:
    return AwsDynamoDBSourceSettings(
        content_type=ContentType.JSON,
        table_name="table_name",
        key={"id": {"S": "123"}},  # type: ignore
        projection_expression="schema",
        **AWS_COMMON_KWARGS
    )

@pytest.fixture
def custom_source_settings() -> CustomSourceSettings:
    return CustomSourceSettings(
        content_type=None,
        context=None
    )

# -----------------------------
# ContentTypeResolver tests
# -----------------------------
@pytest.mark.parametrize(
    "filename,expected",
    [
        ("file.yaml", ContentType.YAML),
        ("file.json", ContentType.JSON),
        ("file.toml", ContentType.TOML),
    ]
)
def test_resolve_local_file_types(tmp_path, filename, expected):
    """Ensure local files resolve content type based on extension."""
    file = tmp_path / filename
    file.write_text("dummy")
    settings = LocalSourceSettings(path=str(file), content_type=None)
    resolver = ContentTypeResolver()
    assert resolver.resolve(settings) == expected

def test_resolve_local_file_unknown_extension_raises(tmp_path):
    """Unknown extension should raise ContentTypeResolutionError."""
    file = tmp_path / "file.unknown"
    file.write_text("dummy")
    settings = LocalSourceSettings(path=str(file), content_type=None)
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)

@pytest.mark.parametrize(
    "settings_fixture,attr,expected_type",
    [
        ("s3_settings", "key", ContentType.YAML),
        ("aws_secrets_manager_settings", "secret_id", ContentType.JSON),
        ("aws_ssm_settings", "parameter_name", ContentType.TOML)
    ]
)
def test_resolve_aws_sources(settings_fixture, attr, expected_type, request):
    """AWS sources with valid extensions resolve correctly."""
    settings = request.getfixturevalue(settings_fixture)
    resolver = ContentTypeResolver()
    assert resolver.resolve(settings) == expected_type

@pytest.mark.parametrize(
    "settings_fixture,attr",
    [
        ("s3_settings", "key"),
        ("aws_secrets_manager_settings", "secret_id"),
        ("aws_ssm_settings", "parameter_name"),
    ]
)
def test_resolve_aws_sources_without_extension_raises(settings_fixture, attr, request):
    """AWS sources missing extensions should raise ContentTypeResolutionError."""
    settings = request.getfixturevalue(settings_fixture)
    # Update the key/secret/parameter to remove extension
    settings = settings.model_copy(update={attr: "noextension"})
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)

def test_resolve_inline_raises():
    """Inline sources without path should raise ContentTypeResolutionError."""
    settings = InlineSourceSettings(content="hello", content_type=None)
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)

def test_resolve_custom_raises(custom_source_settings):
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(custom_source_settings)

def test_resolve_http_raises():
    """Http sources without path should raise ContentTypeResolutionError."""
    settings = HttpSourceSettings(url="localhost:/", content_type=None)
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)

def test_resolve_aws_dynamodb_raises(aws_dynamodb_settings):
    """DynamoDB sources have no path and should raise ContentTypeResolutionError."""
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(aws_dynamodb_settings)
