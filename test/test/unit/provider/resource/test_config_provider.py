from unittest.mock import Mock

import pytest

from templisafe.parser.config.config_parser import Config
from templisafe.provider.resource.config_provider import ConfigProvider

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def provider() -> ConfigProvider:
    """Return a ConfigProvider instance."""
    return ConfigProvider()


@pytest.fixture
def parser() -> Mock:
    """Mock ConfigParser."""
    return Mock()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_provide_delegates_to_parser(provider: ConfigProvider, parser: Mock):
    """ConfigProvider delegates parsing to the given ConfigParser."""
    payload = "some: config"
    expected_config = Mock(spec=Config)

    parser.parse.return_value = expected_config

    result = provider.provide(payload, parser)

    parser.parse.assert_called_once_with(payload)
    assert result is expected_config
