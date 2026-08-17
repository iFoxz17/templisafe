from unittest.mock import Mock

import pytest

from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.parser.settings.settings_parser_manager import SettingsParserManager
from templisafe.parser.settings.settings_parser_resolver import SettingsParserResolver
from templisafe.settings.settings import SettingsKind

# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def mock_settings_parser_manager():
    return Mock(spec=SettingsParserManager)


@pytest.fixture
def settings_parser_resolver(mock_settings_parser_manager):
    return SettingsParserResolver(settings_parser_manager=mock_settings_parser_manager)


# -----------------------------
# Tests
# -----------------------------


def test_resolve_returns_existing_parser(settings_parser_resolver, mock_settings_parser_manager):
    mock_parser = Mock(spec=SettingsParser)
    mock_settings_parser_manager.get_or_create.return_value = mock_parser

    result = settings_parser_resolver.resolve(SettingsKind.SOURCE_SETTINGS)

    mock_settings_parser_manager.get_or_create.assert_called_once_with(SettingsKind.SOURCE_SETTINGS)
    assert result is mock_parser
