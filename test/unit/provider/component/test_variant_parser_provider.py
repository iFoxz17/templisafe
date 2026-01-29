import pytest
from unittest.mock import Mock

from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.parser.variant.variant_parser_resolver import VariantParserResolver
from templisafe.provider.component.variant_parser_provider import VariantParserProvider
from templisafe.settings.variant_parser_settings import VariantParserSettings


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        Mock(spec=VariantParser),
        Mock(spec=VariantParserSettings),
    ],
)
def test_provide_delegates_to_resolver(input_value):
    # Arrange
    mock_resolver = Mock(spec=VariantParserResolver)
    mock_parser = Mock(spec=VariantParser)
    mock_resolver.resolve.return_value = mock_parser

    provider = VariantParserProvider(mock_resolver)

    # Act
    result = provider.provide(input_value)

    # Assert
    mock_resolver.resolve.assert_called_once_with(input_value)
    assert result is mock_parser
