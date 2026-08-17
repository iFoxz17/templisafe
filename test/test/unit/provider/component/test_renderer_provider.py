from unittest.mock import Mock

import pytest

from templisafe.provider.component.renderer_provider import RendererProvider
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_resolver import RendererResolver


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        Mock(spec=Renderer),
        Mock(spec=RendererSettings),
    ],
)
def test_provide_delegates_to_resolver(input_value):
    # Arrange
    mock_resolver = Mock(spec=RendererResolver)
    mock_renderer = Mock(spec=Renderer)
    mock_resolver.resolve.return_value = mock_renderer

    provider = RendererProvider(mock_resolver)

    # Act
    result = provider.provide(input_value)

    # Assert
    mock_resolver.resolve.assert_called_once_with(input_value)
    assert result is mock_renderer
