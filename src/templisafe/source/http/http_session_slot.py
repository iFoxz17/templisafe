from dataclasses import dataclass
from typing import Generic, TypeVar

# Generic type for session (requests.Session or aiohttp.ClientSession)
T = TypeVar("T")

@dataclass(slots=True)
class HttpSessionSlot(Generic[T]):
    """
    Represents a single HTTP session with a reference count.

    Works for both synchronous (requests.Session) and asynchronous (aiohttp.ClientSession) pools.

    Attributes:
        session (T): The underlying session object.
        ref_count (int): Number of active users currently holding this session.
    """
    session: T
    ref_count: int = 0