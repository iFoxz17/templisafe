import pytest

from templisafe.core.metadata import Metadata, MetaValue

# ============================================================
# MetaValue
# ============================================================


def test_metavalue_basic():
    mv = MetaValue(value=42, description="The answer")
    assert mv.value == 42
    assert mv.description == "The answer"
    assert mv.type is int


# ============================================================
# Metadata creation and access
# ============================================================


def test_metadata_creation_and_getitem():
    meta = Metadata({"a": MetaValue(1), "b": MetaValue("x", "letter")})

    assert meta["a"].value == 1
    assert meta["b"].description == "letter"
    assert len(meta) == 2
    assert set(meta.keys()) == {"a", "b"}
    assert list(meta.values())[0].value in {1, "x"}
    assert list(meta.items())[1][0] in {"a", "b"}


def test_metadata_iteration():
    meta = Metadata({"x": MetaValue(1), "y": MetaValue(2)})
    keys = [k for k in meta]
    assert set(keys) == {"x", "y"}


# ============================================================
# Metadata get with default
# ============================================================


def test_metadata_get_default():
    meta = Metadata({"x": MetaValue(10)})
    # Existing key
    assert meta.get("x").value == 10
    # Missing key returns default
    default_mv = MetaValue("default")
    assert meta.get("missing", default_mv).value == "default"


# ============================================================
# Read-only enforcement
# ============================================================


def test_metadata_read_only_assignment():
    meta = Metadata({"a": MetaValue(1)}, read_only=True)
    with pytest.raises(TypeError):
        meta["b"] = MetaValue(2)


def test_metadata_mutable_assignment():
    meta = Metadata({"a": MetaValue(1)}, read_only=False)
    meta["b"] = MetaValue(2)
    assert meta["b"].value == 2
    # Can overwrite existing key
    meta["a"] = MetaValue(42)
    assert meta["a"].value == 42


# ============================================================
# Empty Metadata
# ============================================================


def test_metadata_empty():
    meta = Metadata()
    assert len(meta) == 0
    assert list(meta.keys()) == []
    assert list(meta.values()) == []
    assert list(meta.items()) == []
    assert meta.get("any") is None
