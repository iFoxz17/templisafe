from _pytest.config import Config
from _pytest.nodes import Item

FOLDER: str = "test/unit/renderer"
MARK: str = "renderer"

def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Automatically mark all tests in this folder as 'renderer'."""
    for item in items:
        if FOLDER in str(item.fspath).replace("\\", "/"):
            item.add_marker(MARK)
