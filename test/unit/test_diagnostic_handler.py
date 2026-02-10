import pytest
from templisafe.util import DiagnosticPolicy, DiagnosticLevel
from templisafe.diagnostic_handler import DiagnosticHandler

class TestException(Exception):
    pass


@pytest.fixture(autouse=True)
def reset_singleton():
    # Reset singleton between tests
    DiagnosticHandler._instance = None
    yield
    DiagnosticHandler._instance = None

def test_double_creation_raises() -> None:
    DiagnosticHandler.create()
    with pytest.raises(RuntimeError):
        DiagnosticHandler.create()

def test_get_or_create_without_creation() -> None:
    handler = DiagnosticHandler.get_or_create()
    assert isinstance(handler, DiagnosticHandler)

@pytest.mark.parametrize(
    "policy, level, exception_cls, should_raise",
    [
        (DiagnosticPolicy.IGNORE, DiagnosticLevel.DEBUG, None, False),
        (DiagnosticPolicy.IGNORE, DiagnosticLevel.WARNING, None, False),
        (DiagnosticPolicy.IGNORE, DiagnosticLevel.ERROR, None, False),
        (DiagnosticPolicy.LOG, DiagnosticLevel.DEBUG, None, False),
        (DiagnosticPolicy.LOG, DiagnosticLevel.WARNING, None, False),
        (DiagnosticPolicy.LOG, DiagnosticLevel.ERROR, TestException, True),
        (DiagnosticPolicy.STRICT, DiagnosticLevel.DEBUG, None, False),
        (DiagnosticPolicy.STRICT, DiagnosticLevel.WARNING, TestException, True),
        (DiagnosticPolicy.STRICT, DiagnosticLevel.ERROR, TestException, True),
    ],
)
def test_handle_exceptions(policy, level, exception_cls, should_raise) -> None:
    handler = DiagnosticHandler.create(policy)

    if should_raise:
        with pytest.raises(TestException):
            handler.handle("test", level, exception_cls=exception_cls)
    else:
        handler.handle("test", level, exception_cls=exception_cls)
