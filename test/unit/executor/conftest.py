from _pytest.config import Config
from _pytest.nodes import Item

FOLDER: str = "test/unit/executor"
MARK: str = "executor"

def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Automatically mark all tests in this folder as 'executor'."""
    for item in items:
        if FOLDER in str(item.fspath).replace("\\", "/"):
            item.add_marker(MARK)
