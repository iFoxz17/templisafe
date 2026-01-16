import pytest
from unittest.mock import create_autospec

from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_manager import (
    CompilerFactory,
    CompilerManager,
)

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def settings():
    return create_autospec(CompilerSettings, instance=True)

@pytest.fixture
def compiler():
    return create_autospec(Compiler, instance=True)

# ------------------------------------------------------------------
# CompilerFactory tests
# ------------------------------------------------------------------

def test_factory_creates_compiler(settings):
    factory = CompilerFactory()

    compiler = factory.create(settings)

    assert isinstance(compiler, Compiler)
    # Compiler should be constructed with the provided settings
    assert compiler._settings is settings

# ------------------------------------------------------------------
# CompilerManager tests
# ------------------------------------------------------------------

def test_get_or_create_creates_new_compiler(settings):
    manager = CompilerManager()

    compiler = manager.get_or_create(settings)

    assert isinstance(compiler, Compiler)
    assert compiler._settings is settings
    assert settings in manager


def test_get_or_create_returns_cached_instance(settings):
    manager = CompilerManager()

    c1 = manager.get_or_create(settings)
    c2 = manager.get_or_create(settings)

    assert c1 is c2  # same instance reused


def test_contains_returns_false_when_not_present(settings):
    manager = CompilerManager()

    assert settings not in manager


def test_contains_returns_true_when_present(settings):
    manager = CompilerManager()
    manager.get_or_create(settings)

    assert settings in manager


def test_preseeded_compilers_are_used(settings, compiler):
    manager = CompilerManager(
        compilers={settings: compiler}
    )

    result = manager.get_or_create(settings)

    assert result is compiler
