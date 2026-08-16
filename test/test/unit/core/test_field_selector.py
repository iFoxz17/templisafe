# test_field_selector.py
from dataclasses import dataclass

import pytest

from templisafe.core.field_selector import FieldSelector


# ------------------------------
# Dummy classes for testing
# ------------------------------
class DummySourceSettings:
    """Mock source settings."""

    def __init__(self, name: str):
        self.name = name


class DummySource:
    """Mock source object."""

    def __init__(self, id: int):
        self.id = id


@dataclass
class DummyTask:
    a: int
    b: str
    src: DummySource
    settings: DummySourceSettings


# ------------------------------
# Tests
# ------------------------------
def test_field_selector_select_by_type() -> None:
    selector = FieldSelector()
    settings = DummySourceSettings(name="cfg")
    src = DummySource(id=42)
    task = DummyTask(a=1, b="x", src=src, settings=settings)

    result = selector.select_by_type(task, types=(DummySource, DummySourceSettings))
    assert result == {
        "src": src,
        "settings": settings,
    }, "Should only select fields of the given types"


def test_field_selector_ignores_other_types() -> None:
    selector = FieldSelector()
    settings = DummySourceSettings(name="cfg")
    src = DummySource(id=42)
    task = DummyTask(a=1, b="x", src=src, settings=settings)

    # Select only DummySource fields
    result = selector.select_by_type(task, types=(DummySource,))
    assert result == {"src": src}, "Should ignore fields not of the selected type"


def test_field_selector_non_dataclass_raises() -> None:
    selector = FieldSelector()
    with pytest.raises(TypeError):
        selector.select_by_type(obj={"a": 1}, types=(DummySource,))
