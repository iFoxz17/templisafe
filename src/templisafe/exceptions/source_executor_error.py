from templisafe.settings.source_executor_settings import SourceExecutorStrategy


class SourceExecutorError(Exception):
    """Base class for source executors-related exceptions."""

    pass


class UnsupportedExecutorStrategy(SourceExecutorError):
    """Raised when trying to instantiate a source executor that is not supported."""

    __slots__: tuple[str, ...] = ("strategy",)

    def __init__(self, strategy: SourceExecutorStrategy) -> None:
        self._strategy = strategy
        super().__init__(f"Missing source executor implementation for strategy: {strategy!r}")
