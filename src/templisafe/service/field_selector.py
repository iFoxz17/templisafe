from dataclasses import fields, is_dataclass
from typing import Any

class FieldSelector:

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def select_by_type(
        self,
        obj: Any,
        types: tuple[type, ...]
    ) -> dict[str, Any]:

        if not is_dataclass(obj):
            raise TypeError(f"Expected a dataclass instance, got {type(obj)}")

        return {
            f.name: getattr(obj, f.name)
            for f in fields(obj)
            if isinstance(getattr(obj, f.name), types)
        }