from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ItemsView, Iterator, KeysView, Mapping, ValuesView

# ============================================================
# MetaValue
# ============================================================


@dataclass(frozen=True, slots=True)
class MetaValue:
    """
    Represents a single metadata entry for a field.
    """

    value: Any
    description: str | None = None

    @property
    def type(self) -> type:
        return type(self.value)


# ============================================================
# Metadata container
# ============================================================


@dataclass(frozen=True, slots=True)
class Metadata(Mapping[str, MetaValue]):
    """
    Container for all metadata of a field.
    Frozen dataclass with slots, but allows optional mutable dict-like assignment
    controlled by read_only flag.
    """

    _entries: dict[str, MetaValue] = field(default_factory=dict)
    read_only: bool = True

    def __init__(self, entries: dict[str, MetaValue] | None = None, read_only: bool = True) -> None:
        object.__setattr__(self, "_entries", entries.copy() if entries else {})
        object.__setattr__(self, "read_only", read_only)

    # ----------------------
    # Mapping interface
    # ----------------------
    def __getitem__(self, key: str) -> MetaValue:
        return self._entries[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def keys(self) -> KeysView[str]:
        return self._entries.keys()

    def values(self) -> ValuesView[MetaValue]:
        return self._entries.values()

    def items(self) -> ItemsView[str, MetaValue]:
        return self._entries.items()

    def get(self, key: str, default: Any = None) -> MetaValue | Any:
        return self._entries.get(key, default)

    # ----------------------
    # Dict-like assignment
    # ----------------------
    def __setitem__(self, key: str, value: MetaValue) -> None:
        if self.read_only:
            raise TypeError(f"Cannot assign to read-only Metadata (attempted key '{key}')")
        self._entries[key] = value


__all__ = ["Metadata", "MetaValue"]
