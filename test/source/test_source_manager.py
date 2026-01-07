import pytest
from sqltemplater.util.util import ContentType
from sqltemplater.source.source_manager import SourceFactory, SourceManager
from sqltemplater.source.source import SourceSettings
from sqltemplater.source.local_source import LocalSource, LocalSourceSettings
from sqltemplater.exceptions.source_error import UnsupportedSourceError

def test_source_factory_create_known():
    settings = LocalSourceSettings(content_type=ContentType.YAML, path="/tmp/file.txt")
    factory = SourceFactory()
    source = factory.create(settings)
    assert isinstance(source, LocalSource)
    assert source._settings == settings

def test_source_factory_create_unknown():
    class DummySettings(SourceSettings):
        pass

    settings = DummySettings(content_type=ContentType.JINJA)
    factory = SourceFactory()
    with pytest.raises(UnsupportedSourceError) as exc_info:
        factory.create(settings)
    assert str(settings) in str(exc_info.value)

def test_source_manager_get_or_create_creates():
    settings = LocalSourceSettings(content_type=ContentType.YAML, path="/tmp/file.txt")
    manager = SourceManager()
    source = manager.get_or_create(settings)
    assert isinstance(source, LocalSource)
    # Getting it again returns the same instance
    source2 = manager.get_or_create(settings)
    assert source is source2

def test_source_manager_contains():
    settings = LocalSourceSettings(content_type=ContentType.YAML, path="/tmp/file.txt")
    manager = SourceManager()
    assert settings not in manager
    manager.get_or_create(settings)
    assert settings in manager

def test_source_manager_custom_sources():
    # Prepopulate manager with a custom source
    settings = LocalSourceSettings(content_type=ContentType.YAML, path="/tmp/file.txt")
    source = LocalSource(settings)
    manager = SourceManager(sources={settings: source})
    assert manager.get_or_create(settings) is source
    assert settings in manager
