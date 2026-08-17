import pytest
from overrides import overrides

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import UnsupportedSourceError
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.source.custom_source_settings import CustomSourceSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.inline_source import InlineSource
from templisafe.source.local_source import LocalSource
from templisafe.source.source import Source
from templisafe.source.source_manager import SourceManager
from templisafe.source.source_resolver import SourceResolver


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def source_manager():
    """SourceManager with caching enabled."""
    settings = ManagerSettings.create(cache=True)
    return SourceManager(settings=settings)


@pytest.fixture
def source_resolver(source_manager):
    """SourceResolver using the SourceManager."""
    return SourceResolver(source_manager=source_manager)


@pytest.fixture
def local_settings(tmp_path):
    """LocalSourceSettings fixture pointing to a YAML file."""
    file = tmp_path / "file.yaml"
    file.write_text("dummy")
    return SourceSettings.create(kind="local", path=str(file), content_type=None)


@pytest.fixture
def inline_settings():
    """InlineSourceSettings fixture with some text content."""
    return SourceSettings.create(kind="inline", content="some content", content_type="text")


@pytest.fixture
def custom_source_settings() -> CustomSourceSettings:
    return CustomSourceSettings(content_type=ContentType.TEXT, context=None)


# -----------------------------
# Tests
# -----------------------------
def test_resolve_local_source(source_resolver: SourceResolver, local_settings):
    """SourceResolver converts LocalSourceSettings into LocalSource with content_type filled."""
    source = source_resolver.resolve(local_settings)
    assert isinstance(source, LocalSource)
    assert source._settings.content_type == ContentType.YAML


def test_resolve_inline_source(source_resolver: SourceResolver, inline_settings):
    """SourceResolver converts InlineSourceSettings into InlineSource with content_type filled."""
    source = source_resolver.resolve(inline_settings)
    assert isinstance(source, InlineSource)
    assert source._settings.content_type == ContentType.TEXT


def test_resolve_already_source_returns_itself(source_resolver, local_settings):
    """If input is already a Source, resolve returns it unchanged."""
    source = source_resolver.resolve(local_settings)
    resolved_again = source_resolver.resolve(source)
    assert resolved_again is source


def test_resolve_optional_none_returns_none(source_resolver: SourceResolver):
    """resolve_optional returns None if input is None."""
    assert source_resolver.resolve_optional(None) is None


def test_resolve_optional_source_returns_source(source_resolver: SourceResolver, inline_settings):
    """resolve_optional resolves a SourceSettings object normally."""
    source = source_resolver.resolve_optional(inline_settings)
    assert isinstance(source, InlineSource)
    assert source._settings.content_type == ContentType.TEXT


def test_resolve_custom_source_settings_raises(source_resolver: SourceResolver, custom_source_settings):
    with pytest.raises(UnsupportedSourceError):
        _ = source_resolver.resolve_optional(custom_source_settings)


def test_resolve_custom_source_returns_source(source_resolver: SourceResolver, custom_source_settings):
    class CustomSource(Source):
        @overrides
        def read(self) -> str:
            assert isinstance(self._settings, CustomSourceSettings)
            return self._settings.context

    custom_source = CustomSource(custom_source_settings)
    source = source_resolver.resolve_optional(custom_source)
    assert isinstance(source, CustomSource)
    assert source._settings.content_type == ContentType.TEXT
    assert source is custom_source
