import pytest

from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.parser.variant.variant_parser_manager import (
    VariantParserFactory,
    VariantParserManager,
)
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings


# -----------------------------
# VariantParserManager fixture (cache enabled and disabled)
# -----------------------------
@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def variant_parser_manager(request) -> VariantParserManager:
    """Create a VariantParserManager with caching enabled or disabled."""
    settings = ManagerSettings(cache=request.param)
    return VariantParserManager(settings=settings)


# -----------------------------
# VariantParserSettings fixtures
# -----------------------------
@pytest.fixture
def default_variant_settings() -> VariantParserSettings:
    """Return default VariantParserSettings."""
    return VariantParserSettings.create()


@pytest.fixture
def custom_variant_settings(
    default_variant_settings: VariantParserSettings,
) -> VariantParserSettings:
    """Return custom VariantParserSettings."""
    # Create a modified copy, e.g., change the top-level key
    return default_variant_settings.model_copy(update={"variants_key": "custom_variants"})


# -----------------------------
# VariantParserFactory tests
# -----------------------------
@pytest.mark.parametrize("settings_fixture", ["default_variant_settings", "custom_variant_settings"])
def test_factory_creates_variant_parser(settings_fixture, request):
    """VariantParserFactory returns a VariantParser instance for the given settings."""
    settings = request.getfixturevalue(settings_fixture)
    parser = VariantParserFactory().create(settings)

    assert isinstance(parser, VariantParser)
    assert parser._settings == settings


# -----------------------------
# VariantParserManager caching behavior
# -----------------------------
def test_manager_caching_behavior(
    default_variant_settings,
    custom_variant_settings,
    variant_parser_manager: VariantParserManager,
):
    """Test that VariantParserManager caches parsers only if caching is enabled."""
    manager = variant_parser_manager

    # Default settings
    parser1 = manager.get_or_create(default_variant_settings)
    parser2 = manager.get_or_create(default_variant_settings)

    if manager._settings.cache:
        assert parser1 is parser2
        assert default_variant_settings in manager
    else:
        assert parser1 is not parser2
        assert default_variant_settings not in manager

    # Custom settings
    parser3 = manager.get_or_create(custom_variant_settings)
    parser4 = manager.get_or_create(custom_variant_settings)

    if manager._settings.cache:
        assert parser3 is parser4
        assert custom_variant_settings in manager
    else:
        assert parser3 is not parser4
        assert custom_variant_settings not in manager
