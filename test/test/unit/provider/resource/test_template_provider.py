from unittest.mock import Mock

import pytest

from templisafe.engine.template_engine import TemplateEngine
from templisafe.parser.template.template_parser import Template, TemplateParser
from templisafe.provider.resource.template_provider import TemplateProvider

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def provider() -> TemplateProvider:
    """Return a TemplateProvider instance."""
    return TemplateProvider()


@pytest.fixture
def engine() -> Mock:
    """Mock TemplateEngine."""
    return Mock(spec=TemplateEngine)


@pytest.fixture
def parser() -> Mock:
    """Mock TemplateParser."""
    return Mock(spec=TemplateParser)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_provide_extracts_variables_and_delegates_parsing(
    provider: TemplateProvider,
    engine: Mock,
    parser: Mock,
):
    """TemplateProvider extracts variables and delegates parsing."""
    template_str = "Hello {{ name }}"
    extracted_vars = {"name"}
    expected_template = Mock(spec=Template)

    engine.extract_variables.return_value = extracted_vars
    parser.parse.return_value = expected_template

    result = provider.provide(template_str, engine, parser)

    engine.extract_variables.assert_called_once_with(template_str)
    parser.parse.assert_called_once_with(template_str, extracted_vars)
    assert result is expected_template
