import pytest
from unittest.mock import Mock
from templisafe.parser.config.config_parser import ConfigParser
from templisafe.parser.config.config_parser_manager import ConfigParserManager
from templisafe.parser.config.config_parser_resolver import ConfigParserResolver
from templisafe.content.content import ContentType

@pytest.fixture
def mock_config_parser_manager():
    return Mock(spec=ConfigParserManager)

@pytest.fixture
def config_parser_resolver(mock_config_parser_manager):
    return ConfigParserResolver(config_parser_manager=mock_config_parser_manager)

def test_resolve_returns_existing_config_parser(config_parser_resolver, mock_config_parser_manager):
    mock_parser = Mock(spec=ConfigParser)
    mock_config_parser_manager.get_or_create.return_value = mock_parser

    result = config_parser_resolver.resolve(ContentType.JSON)

    mock_config_parser_manager.get_or_create.assert_called_once_with(ContentType.JSON)
    assert result is mock_parser
