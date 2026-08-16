import pytest

from templisafe.core.util import DiagnosticPolicy
from templisafe.service.service_orchestrator import ServiceOrchestrator
from templisafe.task.task_validator import TaskValidator
from templisafe.templater import Templater
from templisafe.templater_factory import TemplaterFactory


@pytest.fixture
def factory() -> TemplaterFactory:
    return TemplaterFactory()


def test_create_returns_templater_with_defaults(factory):
    """
    Test that create() returns a Templater with all default settings when no sources are provided.
    """
    templater = factory.create()

    assert isinstance(templater, Templater)
    assert isinstance(templater._task_validator, TaskValidator)
    assert isinstance(templater._service_orchestrator, ServiceOrchestrator)
    assert isinstance(templater._outcome_handler._policy, DiagnosticPolicy)


def test_create_with_invalid_diagnostic_policy_raises(factory):
    """
    Test that an invalid diagnostic_policy string raises a ValueError
    """
    with pytest.raises(ValueError):
        factory.create(diagnostic_policy="not_a_policy")


@pytest.mark.parametrize(
    "policy_str,expected",
    [
        ("ignore", DiagnosticPolicy.IGNORE),
        ("log", DiagnosticPolicy.LOG),
        ("strict", DiagnosticPolicy.STRICT),
    ],
)
def test_create_accepts_valid_diagnostic_policy_string(factory, policy_str, expected):
    templater = factory.create(diagnostic_policy=policy_str)
    assert templater._outcome_handler._policy == expected


def test_create_accepts_diagnostic_policy_enum(factory):
    templater = factory.create(diagnostic_policy=DiagnosticPolicy.STRICT)
    assert templater._outcome_handler._policy == DiagnosticPolicy.STRICT


def test_create_orchestrator_returns_pipeline_with_expected_services(factory):
    templater = factory.create()
    orchestrator = templater._service_orchestrator

    assert hasattr(orchestrator, "_source_service")
    assert hasattr(orchestrator, "_data_service")
    assert hasattr(orchestrator, "_config_service")
    assert hasattr(orchestrator, "_settings_service")
    assert hasattr(orchestrator, "_component_service")
    assert hasattr(orchestrator, "_resource_service")


def test_create_source_service_returns_provider_with_expected_types(factory):
    templater = factory.create()
    source_service = templater._service_orchestrator._source_service

    assert hasattr(source_service, "_source_provider")
    assert hasattr(source_service, "_field_selector")
