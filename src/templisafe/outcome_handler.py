import logging
import warnings

from templisafe.template.template_model import Compilation, Rendering
from templisafe.template.template_model import Outcome
from templisafe.util import DiagnosticPolicy
from templisafe.exceptions.compilation_error import CompilationFailureError
from templisafe.exceptions.rendering_error import RenderingFailureError

class OutcomeHandler:
    """
    Handles outcomes of Compilation, Rendering, Validation and Build processes
    according to a DiagnosticPolicy. Decides logging, warning or raising exceptions.
    """

    def __init__(self, policy: DiagnosticPolicy) -> None:
        self._policy: DiagnosticPolicy = policy

    # -------------------------
    # Compilation
    # -------------------------
    def handle_compilation(self, compilation: Compilation) -> None:
        self._handle_outcome(
            outcome_obj=compilation,
            success_msg="Query compiled successfully",
            warning_msg=f"Query compiled with warnings: {', '.join([d.message for d in compilation.diagnostics])}",
            error_msg="Query compilation failed",
            error_cls=CompilationFailureError
        )

    # -------------------------
    # Rendering
    # -------------------------
    def handle_rendering(self, rendering: Rendering) -> None:
        self._handle_outcome(
            outcome_obj=rendering,
            success_msg="Query rendered successfully",
            warning_msg=f"Query rendered with warnings: {', '.join([d.message for d in rendering.diagnostics])}",
            error_msg="Query rendering failed",
            error_cls=RenderingFailureError
        )

    # -------------------------
    # Validation
    # -------------------------
    def handle_validation(self, rendering: Rendering) -> None:
        self.handle_rendering(rendering)

    # -------------------------
    # Private logic
    # -------------------------
    def _handle_outcome(
        self,
        outcome_obj: Compilation | Rendering,
        *,
        success_msg: str,
        warning_msg: str,
        error_msg: str,
        error_cls: type[Exception]
    ) -> None:
        if self._policy is DiagnosticPolicy.IGNORE:
            return
        
        match outcome_obj.outcome:
            case Outcome.SUCCESS:
                logging.debug(success_msg)
            case Outcome.WARNING:
                logging.debug(warning_msg)
                if self._policy is DiagnosticPolicy.STRICT:
                    raise error_cls(outcome_obj)
                elif self._policy is DiagnosticPolicy.LOG:
                    warnings.warn(warning_msg, stacklevel=1)
            case Outcome.ERROR:
                logging.debug(error_msg)
                raise error_cls(outcome_obj)
