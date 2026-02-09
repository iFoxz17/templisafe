import logging
import warnings

from templisafe.util import DiagnosticPolicy, DiagnosticLevel

class DiagnosticHandler:
    """
    Centralized diagnostic decision engine.

    This singleton controls how diagnostics are handled across the library
    according to the active diagnostic policy.

    Behavior matrix:

    +----------+--------+----------------------------+
    | Policy   | Level  | Behavior                   |
    +----------+--------+----------------------------+
    | IGNORE   | any    | No action                  |
    | LOG      | DEBUG  | logging.debug(msg)         |
    | LOG      | WARNING| warnings.warn(msg)         |
    | LOG      | ERROR  | raise exception_cls(msg)   |
    | STRICT   | DEBUG  | logging.debug(msg)         |
    | STRICT   | WARNING| raise exception_cls(msg)   |
    | STRICT   | ERROR  | raise exception_cls(msg)   |
    +----------+--------+----------------------------+
    """

    __slots__ = ("_policy",)

    _instance: "DiagnosticHandler | None" = None

    # ------------------------------------------------------------------
    # Singleton interface
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, policy: DiagnosticPolicy) -> "DiagnosticHandler":
        """
        Create the singleton DiagnosticHandler.

        Parameters
        ----------
        policy : DiagnosticPolicy
            The diagnostic policy to apply globally.

        Returns
        -------
        DiagnosticHandler
            The singleton instance.
        """
        if cls._instance is not None:
            raise RuntimeError("DiagnosticHandler singleton already created")
        
        cls._instance = cls.__new__(cls)
        cls._instance._policy = policy
        return cls._instance

    @classmethod
    def get(cls) -> "DiagnosticHandler":
        """
        Get the singleton instance.

        Returns
        -------
        DiagnosticHandler
            The singleton instance.

        Raises
        ------
        RuntimeError
            If the singleton was not created yet.
        """
        if cls._instance is None:
            raise RuntimeError("DiagnosticHandler singleton not created yet")
        return cls._instance

    # ------------------------------------------------------------------
    # Policy accessors
    # ------------------------------------------------------------------
    @property
    def policy(self) -> DiagnosticPolicy:
        """Get the currently active diagnostic policy."""
        return self._policy

    @policy.setter
    def policy(self, policy: DiagnosticPolicy) -> None:
        """Set the diagnostic policy globally."""
        self._policy = policy

    # ------------------------------------------------------------------
    # Core diagnostic handling
    # ------------------------------------------------------------------
    def handle(
        self,
        msg: str,
        level: DiagnosticLevel,
        *,
        exception_cls: type[Exception] | None = None,
        exception_payload: object | None = None,
        warning_stack_level: int = 2,
    ) -> None:
        """
        Handle a diagnostic message according to the active policy.

        Parameters
        ----------
        msg : str
            Diagnostic message to be handled.
        level : DiagnosticLevel
            Severity level of the diagnostic event.
        exception_cls : type[Exception] | None
            Exception class to raise for WARNING or ERROR levels when
            the policy is STRICT or for ERROR in LOG.
        exception_payload : object | None
            Optional payload passed to the exception constructor.
        warning_stack_level : int
            Stack level used when emitting warnings. Defaults to 2.

        Raises
        ------
        Exception
            If the policy is STRICT and `exception_cls` is provided for WARNING or ERROR,
            or if the policy is LOG and the level is ERROR and `exception_cls` is provided.
        """
        policy = self._policy

        if policy is DiagnosticPolicy.IGNORE:
            return

        if level is DiagnosticLevel.DEBUG:
            logging.debug(msg)
            return

        if policy is DiagnosticPolicy.STRICT:
            logging.error(msg)
            if exception_cls is not None:
                raise exception_cls(exception_payload) if exception_payload else exception_cls()
            return

        # LOG policy
        if level is DiagnosticLevel.WARNING:
            warnings.warn(msg, stacklevel=warning_stack_level)
        elif level is DiagnosticLevel.ERROR:
            logging.error(msg)
            if exception_cls is not None:
                raise exception_cls(exception_payload) if exception_payload else exception_cls()

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def debug(self, msg: str) -> None:
        self.handle(msg, DiagnosticLevel.DEBUG)

    def warn(
        self,
        msg: str,
        *,
        exception_cls: type[Exception] | None = None,
        exception_payload: object | None = None,
        warning_stack_level: int = 2,
    ) -> None:
        self.handle(
            msg,
            DiagnosticLevel.WARNING,
            exception_cls=exception_cls,
            exception_payload=exception_payload,
            warning_stack_level=warning_stack_level,
        )

    def error(
        self,
        msg: str,
        *,
        exception_cls: type[Exception] | None = None,
        exception_payload: object | None = None,
        warning_stack_level: int = 2,
    ) -> None:
        self.handle(
            msg,
            DiagnosticLevel.ERROR,
            exception_cls=exception_cls,
            exception_payload=exception_payload,
            warning_stack_level=warning_stack_level,
        )
