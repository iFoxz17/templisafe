import pytest
from unittest.mock import create_autospec

from templisafe.templater_factory import TemplaterFactory
from templisafe.templater import Templater
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind
from templisafe.util import DiagnosticPolicy
from templisafe.source.source import Source


@pytest.fixture
def factory() -> TemplaterFactory:
    return TemplaterFactory()


def test_create_returns_templater_with_defaults(factory):
    """
    Test that create() returns a Templater with all default settings when no sources are provided.
    """
    templater = factory.create()

    assert isinstance(templater, Templater)
    assert isinstance(templater._compiler_default_settings, CompilerSettings)
    assert isinstance(templater._renderer_default_settings, RendererSettings)
    assert isinstance(templater._outcome_handler._policy, DiagnosticPolicy)

def test_create_with_invalid_diagnostic_policy_raises(factory):
    """
    Test that an invalid diagnostic_policy string raises a ValueError
    """
    with pytest.raises(ValueError):
        factory.create(diagnostic_policy="not_a_policy")


@pytest.mark.parametrize("policy_str,expected", [
    ("ignore", DiagnosticPolicy.IGNORE),
    ("log", DiagnosticPolicy.LOG),
    ("strict", DiagnosticPolicy.STRICT),
])
def test_create_accepts_valid_diagnostic_policy_string(factory, policy_str, expected):
    templater = factory.create(diagnostic_policy=policy_str)
    assert templater._outcome_handler._policy == expected


def test_create_accepts_diagnostic_policy_enum(factory):
    templater = factory.create(diagnostic_policy=DiagnosticPolicy.STRICT)
    assert templater._outcome_handler._policy == DiagnosticPolicy.STRICT


def test_create_loader_facade_returns_loader_with_expected_types(factory):
    templater = factory.create()
    loader = templater._loader_facade

    # Loader should have the correct loaders
    assert hasattr(loader, "_template_loader")
    assert hasattr(loader, "_schema_loader")
    assert hasattr(loader, "_variant_loader")

def test_create_source_resolverreturns_resolver_with_expected_types(factory):
    templater = factory.create()
    resolver = templater._source_resolver

    # Loader should have the correct loaders
    assert hasattr(resolver, "_config_loader")
