import pytest

from templisafe.util.util import ContentType
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source.s3_source_settings import S3SourceSettings
from templisafe.source.s3_source import S3Source
from templisafe.source.local_source import LocalSource
from templisafe.source.inline_source import InlineSource
from templisafe.exceptions.source_error import UnsupportedSourceError, ContentTypeResolutionError
from templisafe.source.source_manager import ContentTypeResolver, SourceFactory, SourceManager


# -----------------------------
# S3Source fixtures
# -----------------------------
@pytest.fixture
def s3_settings() -> S3SourceSettings:
    return S3SourceSettings(
        bucket="my-bucket",
        key="my-key.yaml",
        aws_access_key_id="AKIAFAKE",
        aws_secret_access_key="SECRETFAKE",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566"
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


def test_resolve_s3_resource_without_extension_raises(s3_settings: S3SourceSettings):
    settings = s3_settings.model_copy(update={"key": "my-key"})
    
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
    assert isinstance(source, S3Source)
    assert source.bucket == "my-bucket"
    assert source.key == "my-key.yaml"


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
    # content_type should now be filled automatically
    assert source._settings.content_type == ContentType.YAML


def test_manager_contains(tmp_path, s3_settings):
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


