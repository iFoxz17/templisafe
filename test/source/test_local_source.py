import pytest
from pathlib import Path
from sqltemplater.util.util import ContentType
from sqltemplater.source.source import Source
from sqltemplater.source.local_source import LocalSource
from sqltemplater.settings.source_settings import SourceSettings, LocalSourceSettings
from sqltemplater.exceptions.source_error import LocalSourceError

def test_source_instantiation_abstract():
    # Source cannot be instantiated directly
    with pytest.raises(TypeError):
        Source(settings=SourceSettings(content_type="dummy"))  # type: ignore

def test_local_source_initialization(tmp_path):
    # Create a temporary file
    file = tmp_path / "test.txt"
    text: str = "hello world: test"
    file.write_text(text)

    settings = LocalSourceSettings(content_type=ContentType.YAML, path=str(file))
    local_source = LocalSource(settings=settings)

    # Test path property
    # assert local_source.path == str(file)

    # Test read method
    assert local_source.read() == text

def test_local_source_file_not_found(tmp_path):
    settings = LocalSourceSettings(content_type=ContentType.YAML, path=str(tmp_path / "nonexistent.txt"))
    local_source = LocalSource(settings=settings)

    # read should raise LocalSourceError if file does not exist
    with pytest.raises(LocalSourceError) as exc_info:
        local_source.read()
    assert str("nonexistent.txt") in str(exc_info.value)
