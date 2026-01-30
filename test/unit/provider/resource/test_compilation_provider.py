from pydantic import BaseModel
import pytest
from unittest.mock import Mock

from templisafe.template.compiler.compiler import Compiler, Compilation
from templisafe.template.template_model import Template, Schema
from templisafe.provider.resource.compilation_provider import CompilationProvider


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def provider() -> CompilationProvider:
    """Return a CompilationProvider instance."""
    return CompilationProvider()


@pytest.fixture
def template() -> Template:
    """Return a dummy Template instance."""
    return Template(template_str="Hello {{ name }}", vars={"name"})


class DummySchema(BaseModel):
    name: str

@pytest.fixture
def schema() -> Schema:
    """Return a dummy Schema instance."""
    return Schema(DummySchema)


@pytest.fixture
def compiler() -> Compiler:
    """Return a mocked Compiler."""
    compiler_mock = Mock(spec=Compiler)
    compiler_mock.compile.return_value = Mock(Compilation)
    return compiler_mock


# -----------------------------
# Tests
# -----------------------------
def test_provide_compilation(provider: CompilationProvider, template: Template, schema: Schema, compiler: Mock):
    """Provider delegates compilation to the Compiler and returns a Compilation."""
    compilation = provider.provide(template, schema, compiler)

    # Verify type and result
    assert isinstance(compilation, Compilation)
    assert compilation == compiler.compile.return_value

    # Verify that the compiler was called with the correct arguments
    compiler.compile.assert_called_once_with(template, schema)
