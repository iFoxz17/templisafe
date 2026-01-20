import pytest
from unittest.mock import MagicMock

from templisafe.loader.template.template_loader import TemplateLoader, TEMPLATE_PARSER_SETTINGS_YAML
from templisafe.template.template_model import Template
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.engine.template_engine import TemplateEngine


@pytest.fixture
def dummy_engine():
    engine = MagicMock(spec=TemplateEngine)
    # Mock extract_variables to just return a set of placeholder variables
    engine.extract_variables.return_value = {"user_id", "name"}
    return engine


@pytest.fixture
def loader(dummy_engine):
    # Use a dummy TemplateParserSettings with minimal config
    settings = TemplateParserSettings.from_yaml(TEMPLATE_PARSER_SETTINGS_YAML)
    return TemplateLoader(default_engine=dummy_engine, default_settings=settings)


# -------------------------
# Tests
# -------------------------
def test_load_returns_template(loader: TemplateLoader, dummy_engine):
    template_str = "SELECT * FROM users WHERE id = :user_id AND name = :name"

    result = loader.load(template_str)

    # Assertions
    assert isinstance(result, Template)
    assert result.template_str == template_str
    assert result.vars == {"user_id", "name"}

    # Ensure extract_variables was called with the template string
    dummy_engine.extract_variables.assert_called_once_with(template_str)


def test_load_with_custom_engine(loader: TemplateLoader):
    template_str = "SELECT * FROM users WHERE id = :user_id AND name = :name"
    custom_engine = MagicMock(spec=TemplateEngine)
    custom_engine.extract_variables.return_value = {"custom_var"}

    result = loader.load(template_str, engine=custom_engine)

    assert isinstance(result, Template)
    assert result.vars == {"custom_var"}
    custom_engine.extract_variables.assert_called_once_with(template_str)
