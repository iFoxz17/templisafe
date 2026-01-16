import pytest
from templisafe.loader.variant.variant_parser_manager import VariantParserFactory, VariantParserManager
from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.settings.variant_parser_settings import VariantParserSettings


@pytest.fixture
def default_settings() -> VariantParserSettings:
    yaml_config = """
variants_key: variants
default_variants_name: default
variant_name_key: name
bindings_key: bindings
"""
    return VariantParserSettings.from_yaml(yaml_config)


def test_factory_creates_parser(default_settings):
    factory = VariantParserFactory()
    parser = factory.create(default_settings)
    assert isinstance(parser, VariantParser)
    assert parser._settings == default_settings


def test_manager_creates_parser_if_missing(default_settings):
    manager = VariantParserManager()
    assert default_settings not in manager
    parser = manager.get_or_create(default_settings)
    assert isinstance(parser, VariantParser)
    assert default_settings in manager


def test_manager_returns_cached_parser(default_settings):
    manager = VariantParserManager()
    parser1 = manager.get_or_create(default_settings)
    parser2 = manager.get_or_create(default_settings)
    assert parser1 is parser2  # same instance
    assert default_settings in manager


def test_manager_can_accept_initial_parsers(default_settings):
    from templisafe.loader.variant.variant_parser import VariantParser
    initial_parser = VariantParser(default_settings)
    parsers_dict = {default_settings: initial_parser}
    manager = VariantParserManager(parsers_dict)
    parser = manager.get_or_create(default_settings)
    # Should return the pre-initialized parser
    assert parser is initial_parser


def test_manager_contains_method(default_settings):
    manager = VariantParserManager()
    assert default_settings not in manager
    _ = manager.get_or_create(default_settings)
    assert default_settings in manager
