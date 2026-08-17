import pytest

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import LocalSourceError
from templisafe.settings.source.local_source_settings import LocalSourceSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.local_source import LocalSource


# -----------------------------
# LocalSource tests
# -----------------------------
def test_local_source_read(tmp_path):
    file = tmp_path / "test.txt"
    text = "hello world: test"
    file.write_text(text)

    settings: SourceSettings = SourceSettings.create(kind="local", path=str(file), content_type=ContentType.YAML)
    assert isinstance(settings, LocalSourceSettings)
    local_source = LocalSource(settings=settings)

    # read should return file content
    assert local_source.read() == text

    # path property
    assert local_source.path == file


def test_local_source_file_not_found(tmp_path):
    file_path = tmp_path / "nonexistent.txt"
    settings: SourceSettings = SourceSettings.create(kind="local", path=str(file_path), content_type=ContentType.YAML)
    assert isinstance(settings, LocalSourceSettings)
    local_source = LocalSource(settings=settings)

    # read should raise LocalSourceError
    with pytest.raises(LocalSourceError) as exc_info:
        local_source.read()
    assert file_path.name in str(exc_info.value)
