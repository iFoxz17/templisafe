import pytest

from templisafe.source.source_assembler import SourceAssembler, DEFAULT_MANAGER_SETTINGS
from templisafe.source.source_resolver import SourceResolver
from templisafe.source.source_manager import SourceManager
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.settings.manager_settings import ManagerSettings

def test_source_assembler_with_explicit_settings():
    """SourceAssembler.assemble returns a SourceResolver using provided ManagerSettings."""
    assembler = SourceAssembler()
    custom_settings = ManagerSettings(cache=False)

    resolver = assembler.assemble(custom_settings)

    assert isinstance(resolver, SourceResolver)
    assert isinstance(resolver._source_manager, SourceManager)
    assert isinstance(resolver._content_type_resolver, ContentTypeResolver)
    # Check that the SourceManager inside the resolver uses the provided settings
    assert resolver._source_manager._settings == custom_settings

def test_source_assembler_with_default_settings():
    """SourceAssembler.assemble returns a SourceResolver using DEFAULT_MANAGER_SETTINGS if None passed."""
    assembler = SourceAssembler()

    resolver = assembler.assemble()

    assert isinstance(resolver, SourceResolver)
    assert isinstance(resolver._source_manager, SourceManager)
    assert isinstance(resolver._content_type_resolver, ContentTypeResolver)
    # Check that the SourceManager inside the resolver uses DEFAULT_MANAGER_SETTINGS
    assert resolver._source_manager._settings == DEFAULT_MANAGER_SETTINGS
