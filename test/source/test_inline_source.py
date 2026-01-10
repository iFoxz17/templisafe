from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_settings import SourceSettings, InlineSourceSettings
from templisafe.util.util import ContentType


def test_inline_source_initialization_and_read():
    """Test InlineSource initialization and read method."""
    # Create InlineSourceSettings via factory
    content_text = "some inline content"
    settings = SourceSettings.create(
        kind="inline",
        content=content_text,
        content_type=ContentType.YAML
    )

    # Instantiate InlineSource
    assert isinstance(settings, InlineSourceSettings)
    inline_source = InlineSource(settings=settings)

    # content property should return the original content
    assert inline_source.content == content_text

    # read() method should return the same content
    assert inline_source.read() == content_text

    # Ensure content_type is correctly preserved
    assert settings.content_type == ContentType.YAML
