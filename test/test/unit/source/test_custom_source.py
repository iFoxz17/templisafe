from overrides import overrides

from templisafe.content.content import ContentType
from templisafe.settings.source.custom_source_settings import CustomSourceSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.source import Source


class CustomSource(Source):
    def __init__(self, settings: SourceSettings) -> None:
        super().__init__(settings)

    @overrides
    def read(self) -> str:
        assert isinstance(self._settings, CustomSourceSettings)
        return self._settings.context["content"]


def test_custom_source_initialization_and_read():
    """Test InlineSource initialization and read method."""
    content: str = "Hello world!"
    settings = SourceSettings.create(kind="custom", context={"content": content}, content_type="text")

    # Instantiate InlineSource
    assert isinstance(settings, SourceSettings)
    custom_source = CustomSource(settings=settings)

    # content property should return the original content
    assert custom_source.content_type == ContentType.TEXT

    # read() method should return the same content
    assert custom_source.read() == content

    # Ensure content_type is correctly preserved
    assert settings.content_type == ContentType.TEXT
