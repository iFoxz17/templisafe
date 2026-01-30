import pytest
from unittest.mock import Mock

from templisafe.provider.resource.settings_provider import SettingsProvider
from templisafe.parser.config.config_parser import Config
from templisafe.parser.settings.settings_parser import Settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def provider() -> SettingsProvider:
    """Return a SettingsProvider instance."""
    return SettingsProvider()


@pytest.fixture
def parser() -> Mock:
    """Mock SettingsParser."""
    return Mock()


@pytest.fixture
def config() -> Mock:
    """Mock Config instance."""
    return Mock(spec=Config)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_provide_delegates_to_parser(
    provider: SettingsProvider,
    config: Config,
    parser: Mock,
):
    """SettingsProvider delegates parsing to the given SettingsParser."""
    expected_settings = Mock(spec=Settings)
    parser.parse.return_value = expected_settings

    result = provider.provide(config, parser)

    parser.parse.assert_called_once_with(config)
    assert result is expected_settings
