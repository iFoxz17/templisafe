from dataclasses import fields, is_dataclass
from typing import Any
from pydantic import BaseModel

class FieldSelector:
    """Utility class to select fields from a dataclass instance based on their types."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def select_by_type(
        self,
        obj: Any,
        types: tuple[type, ...] | type
    ) -> dict[str, Any]:
        """
        Select fields of a dataclass instance whose values match the specified type(s).

        Parameters
        ----------
        obj : Any
            The dataclass instance from which to extract fields.
        types : type or tuple[type, ...]
            The type or tuple of types used to filter fields. Only fields whose values
            are instances of these types are included in the result.

        Returns
        -------
        dict[str, Any]
            A dictionary mapping field names to their values, including only
            fields whose values match the given type(s).

        Raises
        ------
        TypeError
            If `obj` is not a dataclass instance.
        """

        if isinstance(obj, BaseModel):
            return {
                name: getattr(obj, name)
                for name in obj.model_fields
                if isinstance(getattr(obj, name), types)
            }

        if not is_dataclass(obj):
            raise TypeError(f"Expected a dataclass or Pydantic model instance, got {type(obj)}")

        return {
            f.name: getattr(obj, f.name)
            for f in fields(obj)
            if isinstance(getattr(obj, f.name), types)
        }
