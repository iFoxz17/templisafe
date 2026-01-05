import pytest
from sqltemplater.source.source import Source
from sqltemplater.settings.source_settings import SourceSettings, LocalSourceSettings
from sqltemplater.util.util import ContentType

# -----------------------
# DummySource fixture
# -----------------------
class DummySource(Source):
    """Simulates a Source with a fixed read() value."""
    def __init__(self, content="dummy"):
        self._content = content

    def read(self):
        return self._content

@pytest.fixture
def dummy_source():
    """Provides a fresh DummySource instance."""
    return DummySource()

class DummyLocalSource(Source):
    def __init__(self, settings, content="dummy"):
        self.settings = settings
        self._content = content

    def read(self):
        return self._content
    
@pytest.fixture
def dummy_local_source():
    """Provides a fresh DummyLocalSource instance."""
    return DummyLocalSource(LocalSourceSettings(content_type=ContentType.YAML, path="/tmp/file.txt"))