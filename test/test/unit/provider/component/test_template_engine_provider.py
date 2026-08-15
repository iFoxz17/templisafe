from unittest.mock import Mock

import pytest

from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.provider.component.template_engine_provider import (
    TemplateEngineProvider,
)
from templisafe.settings.template_engine_settings import TemplateEngineSettings


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        Mock(spec=TemplateEngine),
        Mock(spec=TemplateEngineSettings),
    ],
)
def test_provide_delegates_to_resolver(input_value):
    # Arrange
    mock_resolver = Mock(spec=TemplateEngineResolver)
    mock_engine = Mock(spec=TemplateEngine)
    mock_resolver.resolve.return_value = mock_engine

    provider = TemplateEngineProvider(mock_resolver)

    # Act
    result = provider.provide(input_value)

    # Assert
    mock_resolver.resolve.assert_called_once_with(input_value)
    assert result is mock_engine
