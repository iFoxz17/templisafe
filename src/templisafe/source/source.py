from abc import ABC, abstractmethod
from types import TracebackType

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import MissingContentTypeError
from templisafe.settings.source.source_settings import SourceSettings

class Source(ABC):
    """
    Base class for a synchronous data source.

    Lifecycle
    ---------
    1. Create the source: `source = MySource(settings)`
    2. Open resources: `source.open()`
    3. Read content: `data = source.read()`
    4. Release resources: `source.close()`

    Alternatively, use the context manager syntax:

    ```python
    with source as s:
        data = s.read()
    ```

    Notes
    -----
    - Resources of the same source type may be shared internally for efficiency.
    - `open` and `close` must be called in the same execution context (process or thread).
    - `read` can safely be called from threads or other execution contexts once the source is opened.
    """

    def __init__(self, settings: SourceSettings) -> None:
        if settings.content_type is None:
            raise MissingContentTypeError(settings)

        self._settings: SourceSettings = settings
        self.content_type: ContentType = settings.content_type

    def open(self) -> None:
        """
        Acquire any resources required by this source.

        Notes
        -----
        - Multiple sources of the same type may share resources internally.
        - Must be called in the same execution context (process or thread), i.e., not from worker threads.
        """
        pass

    def close(self) -> None:
        """
        Release resources acquired by `open`.

        Notes
        -----
        - Multiple sources of the same type may share resources internally.
        - Must be called in the same execution context (process or thread), i.e., not from worker threads.
        - Safe to call multiple times (idempotent).
        """
        pass

    def __enter__(self) -> "Source":
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.close()
        return False

    @abstractmethod
    def read(self) -> str:
        """
        Retrieve the content of the source synchronously.

        Can be called from threads or the main context.

        Returns
        -------
        str
            The content of the source.
        """
        raise NotImplementedError


class AsyncSource(Source, ABC):
    """
    Base class for an asynchronous data source.

    Lifecycle
    ---------
    1. Create the source: `source = MyAsyncSource(settings)`
    2. Open resources: `await source.aopen()`  ← must be called outside threads
    3. Read content: `data = await source.aread()`  ← can be called inside async tasks
    4. Release resources: `await source.aclose()`  ← must be called outside threads

    Alternatively, use the async context manager syntax:

    ```python
    async with source as s:
        data = await s.aread()
    ```
    """

    async def aopen(self) -> None:
        """Acquire any resources required asynchronously."""
        pass

    async def aclose(self) -> None:
        """Release any asynchronous resources acquired by `aopen`.

        Notes
        -----
        - Safe to call multiple times (idempotent).
        """
        pass

    async def __aenter__(self) -> "AsyncSource":
        await self.aopen()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        await self.aclose()
        return False

    @abstractmethod
    async def aread(self) -> str:
        """
        Retrieve the content of the source asynchronously.

        Can be called from async tasks or the main event loop.

        Returns
        -------
        str
            The content of the source.
        """
        raise NotImplementedError
