import warnings
from types import SimpleNamespace

import pytest

from templisafe.core.outcome_handler import OutcomeHandler
from templisafe.core.util import DiagnosticPolicy
from templisafe.exceptions.compilation_error import CompilationFailureError
from templisafe.exceptions.rendering_error import RenderingFailureError
from templisafe.template.template_model import (
    Compilation,
    Diagnostic,
    Outcome,
    Rendering,
)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def make_diagnostic(outcome: Outcome, msg: str):
    return Diagnostic(level=outcome, message=msg)


def make_compilation(outcome: Outcome):
    return Compilation(outcome=outcome, message="", diagnostics=(make_diagnostic(outcome, "diag1"),))


def make_rendering(outcome: Outcome):
    return Rendering(outcome=outcome, message="", diagnostics=(make_diagnostic(outcome, "diag1"),))


# ---------------------------------------------------------------------
# Compilation handling
# ---------------------------------------------------------------------


def test_compilation_success_ignore_policy_does_nothing():
    handler = OutcomeHandler(DiagnosticPolicy.IGNORE)
    compilation = make_compilation(Outcome.SUCCESS)

    handler.handle_compilation(compilation)  # no exception


def test_compilation_warning_log_policy_emits_warning():
    handler = OutcomeHandler(DiagnosticPolicy.LOG)
    compilation = make_compilation(Outcome.WARNING)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        handler.handle_compilation(compilation)

        assert len(w) == 1
        assert "Query compiled with warnings" in str(w[0].message)


def test_compilation_warning_strict_policy_raises():
    handler = OutcomeHandler(DiagnosticPolicy.STRICT)
    compilation = make_compilation(Outcome.WARNING)

    with pytest.raises(CompilationFailureError):
        handler.handle_compilation(compilation)


def test_compilation_error_always_raises():
    handler = OutcomeHandler(DiagnosticPolicy.LOG)
    compilation = make_compilation(Outcome.ERROR)

    with pytest.raises(CompilationFailureError):
        handler.handle_compilation(compilation)


# ---------------------------------------------------------------------
# Rendering / Validation handling
# ---------------------------------------------------------------------


def test_rendering_warning_log_policy_emits_warning():
    handler = OutcomeHandler(DiagnosticPolicy.LOG)
    rendering = make_rendering(Outcome.WARNING)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        handler.handle_rendering(rendering)

        assert len(w) == 1
        assert "Query rendered with warnings" in str(w[0].message)


def test_rendering_error_raises():
    handler = OutcomeHandler(DiagnosticPolicy.STRICT)
    rendering = make_rendering(Outcome.ERROR)

    with pytest.raises(RenderingFailureError):
        handler.handle_rendering(rendering)


def test_validation_delegates_to_rendering():
    handler = OutcomeHandler(DiagnosticPolicy.STRICT)
    rendering = make_rendering(Outcome.ERROR)

    with pytest.raises(RenderingFailureError):
        handler.handle_validation(rendering)
