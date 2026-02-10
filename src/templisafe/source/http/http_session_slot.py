from dataclasses import dataclass
from typing import Generic, TypeVar

# Generic type for session (requests.Session or aiohttp.ClientSession)
T = TypeVar("T")

@dataclass(slots=True)
class HttpSessionSlot(Generic[T]):
    """Represents a single HTTP session with a reference count."""
    
    session: T
    ref_count: int = 0