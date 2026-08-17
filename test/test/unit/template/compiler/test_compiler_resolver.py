import pytest

from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_manager import (
    CompilerFactory,
    CompilerManager,
)
from templisafe.template.compiler.compiler_resolver import CompilerResolver


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def factory() -> CompilerFactory:
    """Return a CompilerFactory instance."""
    return CompilerFactory()


@pytest.fixture
def manager(factory) -> CompilerManager:
    """CompilerManager without caching."""
    settings = ManagerSettings(cache=False)
    return CompilerManager(settings=settings, factory=factory)


@pytest.fixture
def compiler_settings() -> CompilerSettings:
    """Return a basic CompilerSettings object."""
    return CompilerSettings(index_key="_index")


@pytest.fixture
def resolver(manager, compiler_settings) -> CompilerResolver:
    """CompilerResolver with default compiler settings."""
    return CompilerResolver(default_settings=compiler_settings, compiler_manager=manager)


# -----------------------------
# Tests
# -----------------------------
def test_resolve_already_compiler(resolver: CompilerResolver, compiler_settings: CompilerSettings):
    """If input is already a Compiler, it is returned as-is."""
    compiler1 = resolver._compiler_manager.get_or_create(compiler_settings)
    compiler2 = resolver.resolve(compiler1)
    assert compiler1 is compiler2


def test_resolve_from_settings(resolver: CompilerResolver):
    """If input is CompilerSettings, a new Compiler is created."""
    new_settings = CompilerSettings(index_key="_key_index")
    compiler = resolver.resolve(new_settings)
    assert isinstance(compiler, Compiler)
    assert compiler._settings == new_settings


def test_resolve_default_settings(resolver: CompilerResolver, compiler_settings: CompilerSettings):
    """If input is None, resolver returns a Compiler using default settings."""
    compiler = resolver.resolve()
    assert isinstance(compiler, Compiler)
    assert compiler._settings == compiler_settings


def test_resolve_multiple_compilers(resolver: CompilerResolver):
    """Resolver can create Compilers for different settings independently."""
    settings1 = CompilerSettings(index_key="_key_index_1")
    settings2 = CompilerSettings(index_key="_key_index_2")

    compiler1 = resolver.resolve(settings1)
    compiler2 = resolver.resolve(settings2)

    assert isinstance(compiler1, Compiler)
    assert isinstance(compiler2, Compiler)
    assert compiler1 is not compiler2
    assert compiler1._settings != compiler2._settings
