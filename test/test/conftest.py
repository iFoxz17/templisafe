from _pytest.config import Config
from _pytest.nodes import Item

MARKERS_BY_FOLDER: tuple[tuple[str, str], ...] = (
    ("test/test/integration", "integration"),
    ("test/test/stress", "stress"),
    ("test/test/unit", "unit"),
    ("test/test/unit/core", "core"),
    ("test/test/unit/engine", "engine"),
    ("test/test/unit/executor", "executor"),
    ("test/test/unit/handler", "handler"),
    ("test/test/unit/parser", "parser"),
    ("test/test/unit/parser/config", "config_parser"),
    ("test/test/unit/parser/schema", "schema_parser"),
    ("test/test/unit/parser/settings", "settings_parser"),
    ("test/test/unit/parser/template", "template_parser"),
    ("test/test/unit/parser/variant", "variant_parser"),
    ("test/test/unit/provider", "provider"),
    ("test/test/unit/provider/component", "component_provider"),
    ("test/test/unit/provider/resource", "resource_provider"),
    ("test/test/unit/service", "service"),
    ("test/test/unit/settings", "settings"),
    ("test/test/unit/settings/source/aws", "aws"),
    ("test/test/unit/source", "source"),
    ("test/test/unit/source/aws", "aws"),
    ("test/test/unit/source/http", "http"),
    ("test/test/unit/task", "task"),
    ("test/test/unit/template", "template"),
    ("test/test/unit/template/compiler", "compiler"),
    ("test/test/unit/template/renderer", "renderer"),
)


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    """Automatically apply suite and package markers based on test paths."""
    for item in items:
        item_path = item.path.as_posix()
        for folder, mark in MARKERS_BY_FOLDER:
            if f"/{folder}/" in item_path or item_path.endswith(f"/{folder}"):
                item.add_marker(mark)
