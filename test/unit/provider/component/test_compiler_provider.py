import pytest
from unittest.mock import Mock

from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_resolver import CompilerResolver
from templisafe.provider.component.compiler_provider import CompilerProvider
from templisafe.settings.compiler_settings import CompilerSettings


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        Mock(spec=Compiler),
        Mock(spec=CompilerSettings),
    ],
)
def test_provide_delegates_to_resolver(input_value):
    # Arrange
    mock_resolver = Mock(spec=CompilerResolver)
    mock_compiler = Mock(spec=Compiler)
    mock_resolver.resolve.return_value = mock_compiler

    provider = CompilerProvider(mock_resolver)

    # Act
    result = provider.provide(input_value)

    # Assert
    mock_resolver.resolve.assert_called_once_with(input_value)
    assert result is mock_compiler
