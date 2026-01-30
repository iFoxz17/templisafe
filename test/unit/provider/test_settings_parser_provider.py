from unittest.mock import Mock

from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.parser.settings.settings_parser_resolver import SettingsParserResolver
from templisafe.provider.settings_parser_provider import SettingsParserProvider
from templisafe.settings.settings import SettingsKind


def test_provide_returns_settings_parser():
    # Arrange
    mock_resolver = Mock(spec=SettingsParserResolver)
    mock_parser = Mock(spec=SettingsParser)
    mock_resolver.resolve.return_value = mock_parser

    provider = SettingsParserProvider(settings_parser_resolver=mock_resolver)
    settings_kind = Mock(spec=SettingsKind)

    # Act
    result = provider.provide(settings_kind)

    # Assert
    mock_resolver.resolve.assert_called_once_with(settings_kind)
    assert result is mock_parser
