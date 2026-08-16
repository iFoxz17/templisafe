from typing import Any

import pytest

from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.parser.variant.variant_parser_manager import VariantParserManager
from templisafe.parser.variant.variant_parser_resolver import VariantParserResolver
from templisafe.settings.variant_parser_settings import VariantParserSettings

# -----------------------------
# Fixtures
# -----------------------------

VARIANT_PARSER_SETTINGS_DICT: dict[str, Any] = {
    "variants_key": "variants",
    "variant_name_key": "name",
    "bindings_key": "bindings",
    "default_variants_name": "default",
}


@pytest.fixture
def default_settings() -> VariantParserSettings:
    """Return default VariantParserSettings."""
    return VariantParserSettings(**VARIANT_PARSER_SETTINGS_DICT)


@pytest.fixture
def custom_settings() -> VariantParserSettings:
    """Return custom VariantParserSettings."""
    return VariantParserSettings(**VARIANT_PARSER_SETTINGS_DICT)


@pytest.fixture
def variant_parser_manager() -> VariantParserManager:
    """Return a VariantParserManager instance."""
    return VariantParserManager(settings=DEFAULT_MANAGER_SETTINGS)


@pytest.fixture
def resolver(
    default_settings: VariantParserSettings,
    variant_parser_manager: VariantParserManager,
) -> VariantParserResolver:
    """Return a VariantParserResolver instance."""
    return VariantParserResolver(default_settings, variant_parser_manager)


# -----------------------------
# VariantParserResolver tests
# -----------------------------


def test_resolver_resolve_with_variant_parser(resolver: VariantParserResolver):
    """VariantParserResolver returns the same VariantParser when passed a VariantParser instance."""
    variant_parser = VariantParser(VariantParserSettings(**VARIANT_PARSER_SETTINGS_DICT))
    result = resolver.resolve(variant_parser)

    assert result is variant_parser
    assert isinstance(result, VariantParser)


def test_resolver_resolve_with_settings(resolver: VariantParserResolver, custom_settings: VariantParserSettings):
    """VariantParserResolver returns a VariantParser when passed VariantParserSettings."""
    result = resolver.resolve(custom_settings)

    assert isinstance(result, VariantParser)
    assert result._settings == custom_settings


def test_resolver_resolve_with_none(resolver: VariantParserResolver, default_settings: VariantParserSettings):
    """VariantParserResolver returns a VariantParser with default settings when passed None."""
    result = resolver.resolve(None)

    assert isinstance(result, VariantParser)
    assert result._settings == default_settings


def test_resolver_respects_manager_caching(resolver: VariantParserResolver, custom_settings: VariantParserSettings):
    """VariantParserResolver respects VariantParserManager caching behavior."""
    result1 = resolver.resolve(custom_settings)
    result2 = resolver.resolve(custom_settings)

    assert isinstance(result1, VariantParser)
    assert isinstance(result2, VariantParser)

    # Assumes manager caching is enabled - adjust if caching is disabled
    if resolver._variant_parser_manager._settings.cache:
        assert result1 is result2
        assert custom_settings in resolver._variant_parser_manager
    else:
        assert result1 is not result2
        assert custom_settings not in resolver._variant_parser_manager
