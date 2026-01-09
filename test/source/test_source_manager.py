import pytest
from pathlib import Path

from sqltemplater.util.util import ContentType
from sqltemplater.settings.source_settings import SourceSettings, SourceKind
from sqltemplater.source.source import Source
from sqltemplater.source.local_source import LocalSource
from sqltemplater.source.inline_source import InlineSource
from sqltemplater.exceptions.source_error import UnsupportedSourceError, ContentTypeResolutionError
from sqltemplater.source.source_manager import ContentTypeResolver, SourceFactory, SourceManager


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
def test_get_or_create_caches_sources(tmp_path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=ContentType.YAML)
    manager = SourceManager()

    source1 = manager.get_or_create(settings)
    source2 = manager.get_or_create(settings)
    assert source1 is source2
    assert settings in manager


def test_get_or_create_resolves_content_type(tmp_path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=None)
    manager = SourceManager()

    source = manager.get_or_create(settings)
    # content_type should now be filled automatically
    assert source._settings.content_type == ContentType.YAML


def test_manager_contains(tmp_path):
    file = tmp_path / "file.yaml"
    file.write_text("dummy")

    settings = SourceSettings.create(kind="local", path=str(file), content_type=ContentType.YAML)
    manager = SourceManager()
    manager.get_or_create(settings)
    assert settings in manager
