import pytest

from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_manager import (
    CompilerFactory,
    CompilerManager,
)

# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def factory() -> CompilerFactory:
    """Return a CompilerFactory instance."""
    return CompilerFactory()


@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def manager(request) -> CompilerManager:
    """Return a CompilerManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return CompilerManager(settings=settings)


@pytest.fixture
def compiler_settings() -> CompilerSettings:
    """Return a basic CompilerSettings object."""
    return CompilerSettings(index_key="_index")


# -----------------------------
# CompilerFactory tests
# -----------------------------


def test_factory_creates_compiler(factory: CompilerFactory, compiler_settings: CompilerSettings):
    """CompilerFactory returns a Compiler instance for given settings."""
    compiler = factory.create(compiler_settings)
    assert isinstance(compiler, Compiler)
    assert compiler._settings == compiler_settings


# -----------------------------
# CompilerManager tests
# -----------------------------


def test_manager_get_or_create(manager: CompilerManager, compiler_settings: CompilerSettings):
    """CompilerManager returns Compiler instances and respects caching."""
    compiler1 = manager.get_or_create(compiler_settings)
    compiler2 = manager.get_or_create(compiler_settings)

    assert isinstance(compiler1, Compiler)
    assert isinstance(compiler2, Compiler)

    if manager._settings.cache:
        # Should be the same instance if caching enabled
        assert compiler1 is compiler2
        assert compiler_settings in manager
    else:
        # Should be different instances if caching disabled
        assert compiler1 is not compiler2
        assert compiler_settings not in manager


def test_manager_contains_only_cached_compilers(manager: CompilerManager, compiler_settings: CompilerSettings):
    """__contains__ reflects only cached compilers."""
    # Initially nothing cached
    assert compiler_settings not in manager

    compiler = manager.get_or_create(compiler_settings)

    if manager._settings.cache:
        assert compiler_settings in manager
    else:
        assert compiler_settings not in manager
