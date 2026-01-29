import pytest
from unittest.mock import Mock

from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.schema.schema_parser_resolver import SchemaParserResolver
from templisafe.provider.component.schema_parser_provider import SchemaParserProvider
from templisafe.settings.schema_parser_settings import SchemaParserSettings


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        Mock(spec=SchemaParser),
        Mock(spec=SchemaParserSettings),
    ],
)
def test_provide_delegates_to_resolver(input_value):
    # Arrange
    mock_resolver = Mock(spec=SchemaParserResolver)
    mock_parser = Mock(spec=SchemaParser)
    mock_resolver.resolve.return_value = mock_parser

    provider = SchemaParserProvider(mock_resolver)

    # Act
    result = provider.provide(input_value)

    # Assert
    mock_resolver.resolve.assert_called_once_with(input_value)
    assert result is mock_parser
