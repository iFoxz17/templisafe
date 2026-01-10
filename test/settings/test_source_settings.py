import pytest
from pathlib import Path
from pydantic import ValidationError

from templisafe.util.util import ContentType
from templisafe.settings.source_settings import (
    SourceSettings,
    SourceKind,
)
from templisafe.source.local_source import LocalSource
from templisafe.settings.source_settings import (
    LocalSourceSettings, 
    InlineSourceSettings
)
from templisafe.exceptions.source_error import LocalSourceError

def test_factory_creates_local_source_settings(tmp_path):
    """Test that the factory creates LocalSourceSettings correctly."""
    file_path = tmp_path / "test.yaml"
    file_path.write_text("dummy content")

    settings = SourceSettings.create(
        kind="local",
        path=str(file_path),
    )
    assert isinstance(settings, LocalSourceSettings)
    assert settings.kind == SourceKind.LOCAL
    assert settings.path == str(file_path)
    assert settings.content_type is None

    # Ensure frozen
    with pytest.raises(Exception):
        settings.path = "/tmp/other.yaml"


def test_factory_creates_inline_source_settings():
    """Test that the factory creates InlineSourceSettings correctly."""
    content = "SELECT 1"
    context: dict[str, object] = {
        "kind": "inline",
        "content": content,
        "content_type": ContentType.JINJA,
    }
    settings = SourceSettings.create(**context)

    assert isinstance(settings, InlineSourceSettings)
    assert settings.kind == SourceKind.INLINE
    assert settings.content == content
    assert settings.content_type == ContentType.JINJA

    # Ensure frozen
    with pytest.raises(Exception):
        settings.content = "new content"


def test_factory_invalid_kind():
    """Test that creating with an invalid kind raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid kind"):
        SourceSettings.create(kind="invalid", path="dummy.txt")


def test_factory_missing_required_fields():
    """Test that missing required fields raises a ValueError."""
    # LocalSourceSettings missing 'path'
    with pytest.raises(ValueError, match="Invalid fields"):
        SourceSettings.create(kind="local", content_type=ContentType.YAML)

    # InlineSourceSettings missing 'content'
    with pytest.raises(ValueError, match="Invalid fields"):
        SourceSettings.create(kind="inline", content_type=ContentType.JINJA)


def test_local_source_read_file(tmp_path):
    """Test that LocalSource reads the file content correctly."""
    file_path = tmp_path / "hello.txt"
    content = """schema:
        id: int
    """
    file_path.write_text(content)

    settings = SourceSettings.create(
        kind="local",
        path=str(file_path),
        content_type=ContentType.YAML,
    )
    assert isinstance(settings, LocalSourceSettings)
    local_source = LocalSource(settings=settings)

    # read should return content
    assert local_source.read() == content


def test_local_source_file_not_found(tmp_path):
    """Test that reading a non-existent file raises LocalSourceError."""
    file_path = tmp_path / "missing.txt"
    settings = SourceSettings.create(
        kind="local",
        path=str(file_path),
        content_type=ContentType.YAML,
    )
    assert isinstance(settings, LocalSourceSettings)
    local_source = LocalSource(settings=settings)

    with pytest.raises(LocalSourceError) as exc_info:
        local_source.read()

    # Ensure filename appears in the error message
    assert file_path.name in str(exc_info.value)
