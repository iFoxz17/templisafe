from typing import Any

import pytest

from templisafe.exceptions.settings_error import SettingsConfigError
from templisafe.parser.settings.settings_parser import (
    SettingsParser,
    SourceSettingsParser,
)
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.source.inline_source_settings import InlineSourceSettings

# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def settings_parser() -> SettingsParser:
    return SettingsParser()


@pytest.fixture
def source_settings_parser() -> SourceSettingsParser:
    return SourceSettingsParser()


VALID_COMPILER_SETTINGS_DICT = {"kind": "compiler_settings", "index_key": "_index1"}
INVALID_CONFIGS = [
    [VALID_COMPILER_SETTINGS_DICT],
    ["not", "a", "dict"],
    "string",
    123,
    None,
]


# -----------------------------
# SettingsParser tests
# -----------------------------


def test_settings_parser_parse_valid_dict(settings_parser: SettingsParser):
    """SettingsParser parses a valid dict into a Settings instance."""
    result = settings_parser.parse(VALID_COMPILER_SETTINGS_DICT)

    assert isinstance(result, CompilerSettings)
    assert result.index_key == "_index1"


@pytest.mark.parametrize("invalid_config", INVALID_CONFIGS)
def test_settings_parser_invalid_config_raises(settings_parser: SettingsParser, invalid_config: Any):
    """SettingsParser raises SettingsConfigError if config is not a dict."""
    with pytest.raises(SettingsConfigError):
        settings_parser.parse(invalid_config)  # type: ignore[arg-type]


# -----------------------------
# SourceSettingsParser tests
# -----------------------------

INLINE_SOURCE_CONFIG = {
    "kind": "inline",
    "content": "SELECT 1",
}


def test_source_settings_parser_returns_source_settings(
    source_settings_parser: SourceSettingsParser,
):
    """SourceSettingsParser returns a concrete SourceSettings instance."""
    result = source_settings_parser.parse(INLINE_SOURCE_CONFIG)

    assert isinstance(result, InlineSourceSettings)
    assert result.content == "SELECT 1"


@pytest.mark.parametrize("invalid_config", INVALID_CONFIGS)
def test_source_settings_parser_invalid_config_raises(
    source_settings_parser: SourceSettingsParser,
    invalid_config: Any,
):
    """SourceSettingsParser raises SettingsConfigError if config is not a dict."""
    with pytest.raises(SettingsConfigError):
        source_settings_parser.parse(invalid_config)  # type: ignore[arg-type]
