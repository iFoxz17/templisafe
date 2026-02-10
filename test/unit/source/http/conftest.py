from _pytest.config import Config
from _pytest.nodes import Item

FOLDER: str = "test/unit/source/http"
MARK: str = "http"

def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Automatically mark all tests in this folder as 'http'."""
    for item in items:
        if FOLDER in str(item.fspath).replace("\\", "/"):
            item.add_marker(MARK)
