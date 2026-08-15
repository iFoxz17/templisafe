from unittest.mock import Mock

import pytest

from templisafe.content.content import ContentType
from templisafe.parser.config.config_parser import ConfigParser
from templisafe.parser.config.config_parser_resolver import ConfigParserResolver
from templisafe.provider.config_parser_provider import ConfigParserProvider


def test_provide_returns_parser():
    # Arrange
    mock_resolver = Mock(spec=ConfigParserResolver)
    mock_parser = Mock(spec=ConfigParser)
    mock_resolver.resolve.return_value = mock_parser

    provider = ConfigParserProvider(config_parser_resolver=mock_resolver)
    content_type = Mock(spec=ContentType)

    # Act
    result = provider.provide(content_type)

    # Assert
    mock_resolver.resolve.assert_called_once_with(content_type)
    assert result is mock_parser
