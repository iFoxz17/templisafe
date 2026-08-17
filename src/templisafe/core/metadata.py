from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView


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

    def __setitem__(self, key: str, value: MetaValue) -> None:
        if self.read_only:
            raise TypeError(f"Cannot assign to read-only Metadata (attempted key '{key}')")
        self._entries[key] = value


def metadata_value(metadata: Iterable[Any], key: str) -> Any:
    """Return a raw metadata value from an iterable of annotated metadata objects."""
    for item in metadata:
        if isinstance(item, Metadata):
            value = item.get(key)
            if isinstance(value, MetaValue):
                return value.value
    return None


__all__ = ["Metadata", "MetaValue", "metadata_value"]
