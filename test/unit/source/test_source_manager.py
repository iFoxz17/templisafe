import pytest

from templisafe.settings.source.aws.aws_dynamodb_source_settings import AwsDynamoDBSourceSettings
from templisafe.settings.source.aws.aws_secrets_manager_source_settings import AwsSecretsManagerSourceSettings
from templisafe.settings.source.aws.aws_ssm_parameter_source_settings import AwsSsmParameterSourceSettings
from templisafe.source.aws.aws_secrets_manager_source import AwsSecretsManagerSource
from templisafe.source.aws.aws_ssm_parameter_source import AwsSsmParameterSource
from templisafe.util.util import ContentType
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source.aws.aws_s3_bucket_source_settings import AwsS3BucketSourceSettings
from templisafe.source.aws.aws_s3_bucket_source import AwsS3BucketSource
from templisafe.source.aws.aws_dynamodb_source import AwsDynamoDBSource
from templisafe.source.local_source import LocalSource
from templisafe.source.inline_source import InlineSource
from templisafe.exceptions.source_error import UnsupportedSourceError, ContentTypeResolutionError
from templisafe.source.source_manager import ContentTypeResolver, SourceFactory, SourceManager


AWS_COMMON_KWARGS: dict[str, str] = {
    "aws_access_key_id": "aws_access_key_id",
    "aws_secret_access_key": "aws_secret_access_key",
    "aws_session_token": "aws_session_token",
    "region_name": "us-east-1",
    "endpoint_url": "http://localhost:4566"
}

# -----------------------------
# Aws sources fixtures
# -----------------------------
@pytest.fixture
def s3_settings() -> AwsS3BucketSourceSettings:
    return AwsS3BucketSourceSettings(
        content_type=None,
        bucket="my-bucket",
        key="my-key.yaml",
        **AWS_COMMON_KWARGS
    )


@pytest.fixture
def aws_secrets_manager_settings() -> AwsSecretsManagerSourceSettings:
    return AwsSecretsManagerSourceSettings(
        content_type=None,
        secret_id="secret_id.json",
        version_id="version_id",
        version_stage="version_stage",
        **AWS_COMMON_KWARGS
    )

@pytest.fixture
def aws_ssm_settings() -> AwsSsmParameterSourceSettings:
    return AwsSsmParameterSourceSettings(
        content_type=None,
        parameter_name="parameter_name.toml",
        with_decryption=True,
        **AWS_COMMON_KWARGS
    )

@pytest.fixture
def aws_dynamodb_settings() -> AwsDynamoDBSourceSettings:
    return AwsDynamoDBSourceSettings(
        content_type=ContentType.JSON,
        table_name="table_name",
        key={"id": {"S": "123"}},      # type: ignore
        projection_expression="schema",
        **AWS_COMMON_KWARGS
    )


# -----------------------------
# ContentTypeResolver tests
# -----------------------------
def test_resolve_local_file(tmp_path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=None)

    resolver = ContentTypeResolver()
    content_type = resolver.resolve(settings)
    assert content_type == ContentType.YAML

def test_resolve_s3_resource_with_extension(s3_settings):
    resolver = ContentTypeResolver()
    content_type = resolver.resolve(s3_settings)
    assert content_type == ContentType.YAML

def test_resolve_s3_resource_without_extension_raises(s3_settings: AwsS3BucketSourceSettings):
    settings = s3_settings.model_copy(update={"key": "my-key"})
    
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)

def test_resolve_aws_secrets_manager_resource_with_extension(aws_secrets_manager_settings):
    resolver = ContentTypeResolver()
    content_type = resolver.resolve(aws_secrets_manager_settings)
    assert content_type == ContentType.JSON

def test_resolve_aws_secrets_manager_resource_without_extension_raises(aws_secrets_manager_settings: AwsSecretsManagerSourceSettings):
    settings = aws_secrets_manager_settings.model_copy(update={"secret_id": "my-secret_id"})
    
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)

def test_resolve_aws_dynamodb_resource_without_extension_raises(aws_dynamodb_settings: AwsSsmParameterSourceSettings):
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(aws_dynamodb_settings)

def test_resolve_aws_ssm_resource_with_extension(aws_ssm_settings):
    resolver = ContentTypeResolver()
    content_type = resolver.resolve(aws_ssm_settings)
    assert content_type == ContentType.TOML

def test_resolve_aws_ssm_resource_without_extension_raises(aws_ssm_settings: AwsSsmParameterSourceSettings):
    settings = aws_ssm_settings.model_copy(update={"parameter_name": "parameter_name"})
    
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)


def test_resolve_inline_raises():
    settings = SourceSettings.create(kind="inline", content="hello", content_type=None)

    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)


def test_resolve_unknown_extension(tmp_path):
    file = tmp_path / "file.unknown"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=None)
    resolver = ContentTypeResolver()
    with pytest.raises(ContentTypeResolutionError):
        resolver.resolve(settings)


# -----------------------------
# SourceFactory tests
# -----------------------------
def test_factory_creates_local_source(tmp_path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=ContentType.YAML)
    factory = SourceFactory()
    source = factory.create(settings)
    assert isinstance(source, LocalSource)


def test_factory_creates_inline_source():
    settings = SourceSettings.create(kind="inline", content="text", content_type=ContentType.YAML)
    factory = SourceFactory()
    source = factory.create(settings)
    assert isinstance(source, InlineSource)

def test_factory_creates_s3_source(s3_settings):
    factory = SourceFactory()
    source = factory.create(s3_settings)
    assert isinstance(source, AwsS3BucketSource)
    assert source.bucket == "my-bucket"
    assert source.key == "my-key.yaml"

def test_factory_creates_aws_secrets_manager_source(aws_secrets_manager_settings):
    factory = SourceFactory()
    source = factory.create(aws_secrets_manager_settings)
    assert isinstance(source, AwsSecretsManagerSource)
    assert isinstance(source._settings, AwsSecretsManagerSourceSettings)
    assert source._settings.secret_id == "secret_id.json"
    assert source._settings.aws_access_key_id == "aws_access_key_id"
    assert source._settings.aws_secret_access_key == "aws_secret_access_key"

def test_factory_creates_aws_ssm_source(aws_ssm_settings):
    factory = SourceFactory()
    source = factory.create(aws_ssm_settings)
    assert isinstance(source, AwsSsmParameterSource)
    assert source.parameter_name == "parameter_name.toml"

def test_factory_creates_aws_dynamodb_source(aws_dynamodb_settings):
    factory = SourceFactory()
    source = factory.create(aws_dynamodb_settings)
    assert isinstance(source, AwsDynamoDBSource)
    assert source.content_type == ContentType.JSON
    assert source.table_name == "table_name"
    assert source.key == (('id', "{'S': '123'}"),)

def test_factory_unsupported_source():
    class DummySettings(SourceSettings):
        
        @property
        def kind(self):     # type: ignore
            return None

    dummy = DummySettings()
    factory = SourceFactory()
    with pytest.raises(UnsupportedSourceError):
        factory.create(dummy)


# -----------------------------
# SourceManager tests
# -----------------------------
def test_get_or_create_caches_sources(tmp_path, s3_settings):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=ContentType.YAML)
    manager = SourceManager()

    source1 = manager.get_or_create(settings)
    source2 = manager.get_or_create(settings)
    assert source1 is source2
    assert settings in manager

    source3 = manager.get_or_create(s3_settings)
    source4 = manager.get_or_create(s3_settings)
    assert source3 is source4
    assert s3_settings in manager


def test_get_or_create_resolves_inline_content_type(tmp_path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=None)
    manager = SourceManager()

    source = manager.get_or_create(settings)
    # content_type should now be filled automatically
    assert source._settings.content_type == ContentType.YAML


def test_get_or_create_resolves_s3_content_type(s3_settings):
    manager = SourceManager()

    source = manager.get_or_create(s3_settings)
    # content_type should be filled automatically
    assert source._settings.content_type == ContentType.YAML


def test_get_or_create_resolves_aws_secrets_manager_content_type(aws_secrets_manager_settings):
    manager = SourceManager()

    source = manager.get_or_create(aws_secrets_manager_settings)
    # content_type should be filled automatically
    assert source._settings.content_type == ContentType.JSON


def test_get_or_create_resolves_aws_ssm_content_type(aws_ssm_settings):
    manager = SourceManager()

    source = manager.get_or_create(aws_ssm_settings)
    # content_type should be filled automatically
    assert source._settings.content_type == ContentType.TOML

def test_get_or_create_resolves_aws_dynamodb_content_type(aws_dynamodb_settings):
    manager = SourceManager()

    source = manager.get_or_create(aws_dynamodb_settings)
    # content_type should be filled automatically
    assert source._settings.content_type == ContentType.JSON


def test_manager_contains(
        tmp_path, 
        s3_settings, 
        aws_secrets_manager_settings,
        aws_ssm_settings,
        aws_dynamodb_settings
        ):
    manager = SourceManager()
    
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    local_settings = SourceSettings.create(kind="local", path=str(file))
    manager.get_or_create(local_settings)
    assert local_settings in manager

    inline_settings = SourceSettings.create(kind="inline", content="schema:\n\ta: 1", content_type="yaml")
    manager.get_or_create(inline_settings)
    assert inline_settings in manager

    manager.get_or_create(s3_settings)
    assert s3_settings in manager

    manager.get_or_create(aws_secrets_manager_settings)
    assert aws_secrets_manager_settings in manager

    manager.get_or_create(aws_ssm_settings)
    assert aws_ssm_settings in manager

    manager.get_or_create(aws_dynamodb_settings)
    assert aws_dynamodb_settings in manager

    

