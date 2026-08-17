from typing import Any, Iterable, Union


def dict_to_frozenset(
    data: dict[Any, Union[Any, Iterable[Any]]],
) -> frozenset[tuple[Any, tuple[Any, ...]]]:
    """
    Convert a dictionary into a frozenset of (key, tuple_of_values) pairs.

    Parameters
    ----------
    data : dict[Any, Any | Iterable[Any]]
        Dictionary to convert. Values can be single items or iterables.

    Returns
    -------
    frozenset[tuple[Any, tuple[Any, ...]]]
        Frozenset of key -> tuple(values) pairs.

    Raises
    ------
    TypeError
        If a value is not a single item or an iterable.
    """
    converted = []
    for key, value in data.items():
        if isinstance(value, (list, tuple, set)):
            value_tuple = tuple(value)
        else:
            value_tuple = (value,)
        converted.append((key, value_tuple))
    return frozenset(converted)
