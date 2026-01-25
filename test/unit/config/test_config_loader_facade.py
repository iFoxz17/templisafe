import pytest
from unittest.mock import MagicMock

from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings, TemplateEngineKind
from templisafe.config.config_loader_facade import ConfigLoaderFacade
from templisafe.config.config_loader_manager import ConfigLoaderManager
from templisafe.config.config_loader import ConfigLoader, Config
from templisafe.source.source import Source
from templisafe.settings.settings import Settings
from templisafe.exceptions.config_error import SettingsConfigError

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def mock_loader() -> ConfigLoader:
    loader = MagicMock(spec=ConfigLoader)
    return loader

@pytest.fixture
def mock_manager(mock_loader) -> ConfigLoaderManager:
    manager = MagicMock(spec=ConfigLoaderManager)
    manager.get_or_create.return_value = mock_loader
    return manager

@pytest.fixture
def facade(mock_manager) -> ConfigLoaderFacade:
    return ConfigLoaderFacade(config_loader_manager=mock_manager)

@pytest.fixture
def source() -> Source:
    src = MagicMock(spec=Source)
    src.content_type = "yaml"
    src.read.return_value = "dummy content"
    return src

# -----------------------------
# Tests
# -----------------------------
def test_load_config_returns_loader_result(
        facade: ConfigLoaderFacade, 
        mock_manager: MagicMock, 
        mock_loader: MagicMock, 
        source: MagicMock
        ):
    """load_config returns the result from the resolved loader."""
    mock_loader.load.return_value = {"a": 1, "b": 2}

    result = facade.load_config(source)

    mock_manager.get_or_create.assert_called_once_with(source.content_type)
    mock_loader.load.assert_called_once_with("dummy content")
    assert result == {"a": 1, "b": 2}

def test_load_settings(facade: ConfigLoaderFacade, mock_loader, source):
    """load_settings returns a Settings object when loader returns a dict."""
    mock_loader.load.return_value = {
        "kind": "manager_settings",
        "cache": False
        }

    settings = facade.load_settings(source)

    assert isinstance(settings, ManagerSettings)
    assert settings.cache is False

def test_load_engine_settings(facade: ConfigLoaderFacade, mock_loader, source):
    mock_loader.load.return_value = {
        "kind": "template_engine_settings",
        "engine_kind": "jinja",
        "config": {
            "optmize": True
        }
    }

    settings = facade.load_settings(source)

    assert isinstance(settings, TemplateEngineSettings)
    assert settings.engine_kind == TemplateEngineKind.JINJA

def test_load_settings_raises_error_for_non_dict(facade, mock_loader, source):
    """load_settings raises SettingsConfigError if loader returns a non-dict."""
    mock_loader.load.return_value = ["not", "a", "dict"]

    with pytest.raises(SettingsConfigError):
        _ = facade.load_settings(source)
