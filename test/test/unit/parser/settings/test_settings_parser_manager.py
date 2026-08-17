import pytest

from templisafe.parser.settings.settings_parser import (
    SettingsParser,
    SourceSettingsParser,
)
from templisafe.parser.settings.settings_parser_manager import (
    SettingsParserFactory,
    SettingsParserManager,
)
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.settings import SettingsKind

# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def factory() -> SettingsParserFactory:
    return SettingsParserFactory()


@pytest.fixture(params=[True, False], ids=["cache_enabled", "cache_disabled"])
def manager(request) -> SettingsParserManager:
    settings = ManagerSettings(cache=request.param)
    return SettingsParserManager(settings=settings)


# -----------------------------
# SettingsParserFactory tests
# -----------------------------


@pytest.mark.parametrize(
    "settings_kind, expected_class",
    [
        (SettingsKind.SOURCE_SETTINGS, SourceSettingsParser),
    ],
)
def test_factory_creates_specific_parser(
    factory: SettingsParserFactory,
    settings_kind: SettingsKind,
    expected_class: type,
):
    """SettingsParserFactory returns the correct parser for mapped settings kinds."""
    parser = factory.create(settings_kind)
    assert isinstance(parser, expected_class)


@pytest.mark.parametrize(
    "settings_kind",
    [sk for sk in SettingsKind if sk is not SettingsKind.SOURCE_SETTINGS],
)
def test_factory_falls_back_to_default_parser(
    factory: SettingsParserFactory,
    settings_kind: SettingsKind,
):
    """Unmapped settings kinds fall back to base SettingsParser."""
    parser = factory.create(settings_kind)
    assert isinstance(parser, SettingsParser)
    assert not isinstance(parser, SourceSettingsParser)


# -----------------------------
# SettingsParserManager tests
# -----------------------------


@pytest.mark.parametrize(
    "settings_kind, expected_class",
    [
        (SettingsKind.SOURCE_SETTINGS, SourceSettingsParser),
    ],
)
def test_manager_get_or_create(
    manager: SettingsParserManager,
    settings_kind: SettingsKind,
    expected_class: type,
):
    """SettingsParserManager returns parsers and respects caching behavior."""
    parser1 = manager.get_or_create(settings_kind)
    parser2 = manager.get_or_create(settings_kind)

    assert isinstance(parser1, expected_class)
    assert isinstance(parser2, expected_class)

    if manager._settings.cache:
        assert parser1 is parser2
        assert settings_kind in manager
    else:
        assert parser1 is not parser2
        assert settings_kind not in manager


def test_manager_contains_only_cached_parsers(manager: SettingsParserManager):
    """__contains__ reflects cached parsers only."""
    kind = SettingsKind.SOURCE_SETTINGS

    assert kind not in manager

    _ = manager.get_or_create(kind)

    if manager._settings.cache:
        assert kind in manager
    else:
        assert kind not in manager
