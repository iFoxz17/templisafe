import pytest
from pathlib import Path

from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source.custom_source_settings import CustomSourceSettings
from templisafe.source.source_manager import SourceManager, SourceFactory
from templisafe.source.local_source import LocalSource
from templisafe.source.inline_source import InlineSource
from templisafe.source.http_source import HttpSource
from templisafe.source.aws import *
from templisafe.settings.source import *
from templisafe.exceptions.source_error import UnsupportedSourceError
from templisafe.content.content import ContentType

# -----------------------------
# SourceManager fixture (cache enabled and disabled)
# -----------------------------
@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def source_manager(request) -> SourceManager:
    """Create a SourceManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return SourceManager(settings=settings)

# -----------------------------
# Fixtures for Local, Inline and Http sources
# -----------------------------
@pytest.fixture
def local_settings(tmp_path: Path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")
    return SourceSettings.create(kind="local", path=str(file), content_type=None)

@pytest.fixture
def inline_settings():
    return SourceSettings.create(kind="inline", content="some content", content_type="text")

@pytest.fixture
def http_settings():
    return SourceSettings.create(kind="http", url="localhost:8080/", content_type="json")

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
        content_type=ContentType.TEXT,
        context=None
    )

# -----------------------------
# SourceFactory tests
# -----------------------------
@pytest.mark.parametrize(
    "settings_fixture,expected_class",
    [
        ("local_settings", LocalSource),
        ("inline_settings", InlineSource),
        ("http_settings", HttpSource),
        ("s3_settings", AwsS3BucketSource),
        ("aws_secrets_manager_settings", AwsSecretsManagerSource),
        ("aws_ssm_settings", AwsSsmParameterSource),
        ("aws_dynamodb_settings", AwsDynamoDBSource),
    ]
)
def test_factory_creates_sources(settings_fixture, expected_class, request):
    """SourceFactory returns correct source class for given settings."""
    settings = request.getfixturevalue(settings_fixture)
    source = SourceFactory().create(settings)
    assert isinstance(source, expected_class)
    assert getattr(source, "_settings", None) == settings


def test_factory_custom_source_raises(custom_source_settings):    
    with pytest.raises(UnsupportedSourceError):
        SourceFactory().create(custom_source_settings)


def test_factory_unsupported_source():
    """Unknown settings should raise UnsupportedSourceError."""
    class DummySettings(SourceSettings):
        @property
        def kind(self):  # type: ignore
            return None
        
    with pytest.raises(UnsupportedSourceError):
        SourceFactory().create(DummySettings())

# -----------------------------
# SourceManager caching tests
# -----------------------------
def test_manager_caching_behavior(tmp_path, local_settings, inline_settings, source_manager: SourceManager):
    """Test that SourceManager caches sources only if caching is enabled."""
    # LocalSource
    source1 = source_manager.get_or_create(local_settings)
    source2 = source_manager.get_or_create(local_settings)

    if source_manager._settings.cache:
        assert source1 is source2
        assert local_settings in source_manager
    else:
        assert source1 is not source2
        assert local_settings not in source_manager

    # InlineSource
    source3 = source_manager.get_or_create(inline_settings)
    source4 = source_manager.get_or_create(inline_settings)

    if source_manager._settings.cache:
        assert source3 is source4
        assert inline_settings in source_manager
    else:
        assert source3 is not source4
        assert inline_settings not in source_manager
