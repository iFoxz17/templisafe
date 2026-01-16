import pytest
from unittest.mock import MagicMock

from templisafe.loader.template.template_loader import TemplateLoader, TEMPLATE_PARSER_SETTINGS_YAML
from templisafe.template.template_model import Template
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.engine.template_engine import TemplateEngine
from templisafe.source.source import Source

@pytest.fixture
def dummy_engine():
    engine = MagicMock(spec=TemplateEngine)
    # Mock extract_variables to just return a set of placeholder variables
    engine.extract_variables.return_value = {"user_id", "name"}
    return engine

@pytest.fixture
def dummy_source():
    source = MagicMock(spec=Source)
    source.read.return_value = "SELECT * FROM users WHERE id = :user_id AND name = :name"
    return source

@pytest.fixture
def loader(dummy_engine):
    settings = TemplateParserSettings.from_yaml(TEMPLATE_PARSER_SETTINGS_YAML)
    return TemplateLoader(default_engine=dummy_engine, default_settings=settings)

def test_load_returns_template(loader: TemplateLoader, dummy_source, dummy_engine):
    result = loader.load(dummy_source)
    
    # Assertions
    assert isinstance(result, Template)
    assert result.template_str == dummy_source.read.return_value
    assert result.vars == {"user_id", "name"}
    
    # Ensure extract_variables was called with the template string
    dummy_engine.extract_variables.assert_called_once_with(dummy_source.read.return_value)

def test_load_with_custom_engine(loader: TemplateLoader, dummy_source):
    custom_engine = MagicMock(spec=TemplateEngine)
    custom_engine.extract_variables.return_value = {"custom_var"}
    
    result = loader.load(dummy_source, engine=custom_engine)
    
    assert isinstance(result, Template)
    assert result.vars == {"custom_var"}
    custom_engine.extract_variables.assert_called_once_with(dummy_source.read.return_value)
