from unittest.mock import Mock

import pytest

from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.template.template_parser_resolver import TemplateParserResolver
from templisafe.provider.component.template_parser_provider import (
    TemplateParserProvider,
)
from templisafe.settings.template_parser_settings import TemplateParserSettings


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        Mock(spec=TemplateParserSettings),
    ],
)
def test_provide_delegates_to_resolver(input_value):
    # Arrange
    mock_resolver = Mock(spec=TemplateParserResolver)
    mock_parser = Mock(spec=TemplateParser)
    mock_resolver.resolve.return_value = mock_parser

    provider = TemplateParserProvider(mock_resolver)

    # Act
    result = provider.provide(input_value)

    # Assert
    mock_resolver.resolve.assert_called_once_with(input_value)
    assert result is mock_parser
