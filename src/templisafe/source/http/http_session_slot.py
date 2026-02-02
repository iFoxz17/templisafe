from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(slots=True)
class HttpSessionSlot(Generic[T]):
    """
    Represents a single HTTP session with a reference count.

    This class abstracts the underlying session implementation, allowing it
    to be used interchangeably for synchronous (`requests.Session`) or
    asynchronous (`aiohttp.ClientSession`) session pools.
    """
    session: T
    ref_count: int = 0
